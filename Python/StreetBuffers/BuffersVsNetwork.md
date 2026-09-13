<!---
Fixed width buffers versus street network measures
-->

*AI disclosure -- this post was created via Claude Code using Claude Opus 5. I gave it the idea, the two study sites and my prior blog posts as style examples, and it wrote the code and the draft. I will always disclose when I use AI to heavily write any content on this blog. (I use it for minor copy editing all the time.)*

Buffers are the default way crime analysts define the area around a place. You have a bar, a bus stop, a vacant lot, and you want to know how much crime is nearby, so you draw a circle. Pick 500 feet, pick a quarter mile, pick whatever the ordinance says. Everybody does it, ArcGIS makes it one click, and for a lot of questions it is fine.

This post is about when it is not fine. The short version is that a buffer's denominator is *area*, and area is not the thing that generates crime. Streets are. When the ratio of street to area is stable, buffers and street network measures tell you the same story. When it is not stable, the buffer will hand you a number that looks like a crime rate and is actually a statement about how much water you drew a circle around.

I use two spots in New York City. The first is Canal Street at Broadway, the counterfeit goods market, which has been [there since the 1980s](https://fordhampoliticalreview.org/counterfeit-economies-the-politics-policing-of-canal-street/) and still gets [seven figure NYPD seizures](https://pix11.com/news/crime/nypd-seizes-151m-in-counterfeit-goods-on-canal-street-other-areas-of-lower-manhattan/). It sits in about as clean a street grid as you will find. The second is the middle of the Brooklyn Bridge, where [illegal vending has been an on-and-off enforcement problem](https://brooklyneagle.com/articles/2025/08/27/illegal-vending-resurfaces-on-brooklyn-bridge-despite-city-ban/) since the city banned it from the walkway in 2024. It sits in a river.

[Data and code are on github](https://github.com/apwheele/Blog_Code/tree/master/Python/StreetBuffers).

# The setup

Three years of NYPD complaint data, 2023 through 2025, thefts (petit and grand larceny) and robberies, pulled from the NYC open data Socrata endpoint. That is 49,270 thefts and 2,558 robberies in the bounding box.

For the street network I use `pygris`, which is Kyle Walker's `tigris` ported to python. Set the project up with `uv`:

    uv init
    uv add geopandas pygris networkx matplotlib requests

There is one trap here worth flagging, because it cost me a rewrite. The obvious function is `pygris.roads()`, and it is the wrong one. `roads()` returns whole named streets, so Canal Street comes back as three features, the main one running 2.1 kilometers end to end. You cannot expand a network over that, there is nothing to expand across. What you want is TIGER **edges**, which are split at every intersection and carry `TNIDF` and `TNIDT` node ids -- the topology is already in the file, you do not have to build it by snapping coordinates yourself.

`pygris` does not expose `edges()` the way `tigris` does, but its internal loader will happily take the URL:

    from pygris.helpers import _load_tiger

    url = 'https://www2.census.gov/geo/tiger/TIGER2023/EDGES/tl_2023_36061_edges.zip'
    e = _load_tiger(url, cache=True)
    e = e[(e['ROADFLG'] == 'Y') & (e['MTFCC'].isin(KEEP))]

Same street, 40 edges instead of 3. After filtering to actual travel ways and clipping to the study area that leaves 6,816 segments across Manhattan and Brooklyn. Everything is projected to UTM 18N so the units are meters.

Crimes get assigned to their nearest segment within 50 meters, which picks up 99.0% of them. That is the standard street units setup -- the crime belongs to a block, not to a polygon.

# Buffers around Canal Street

Buffers every 100 meters out to a kilometer, and for each one I take the area, clip the street network to it, and count crimes inside.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/CanalSt_Map.png)

|   Meters |   Area |   % Land |   Street km |   Street km/sq km |   Thefts |   Robberies |   Per sq km |   Per street km |
|---------:|-------:|---------:|------------:|------------------:|---------:|------------:|------------:|----------------:|
|      100 |  0.031 |      100 |        0.68 |              21.6 |      175 |          26 |        6408 |           296.4 |
|      200 |  0.125 |      100 |        3.03 |              24.1 |      782 |          50 |        6631 |           275   |
|      300 |  0.282 |      100 |        6.37 |              22.6 |     1190 |          77 |        4488 |           198.8 |
|      400 |  0.502 |      100 |       11.32 |              22.5 |     1690 |         105 |        3577 |           158.6 |
|      500 |  0.784 |      100 |       17.25 |              22   |     3692 |         168 |        4923 |           223.8 |
|      600 |  1.129 |      100 |       24.84 |              22   |     5663 |         261 |        5246 |           238.5 |
|      700 |  1.537 |      100 |       33.78 |              22   |     6698 |         341 |        4580 |           208.4 |
|      800 |  2.007 |      100 |       43.93 |              21.9 |     9117 |         457 |        4769 |           218   |
|      900 |  2.541 |      100 |       56.04 |              22.1 |    12253 |         577 |        5050 |           228.9 |
|     1000 |  3.137 |      100 |       69.28 |              22.1 |    13855 |         692 |        4638 |           210   |

Look at the `Street km/sq km` column. It is 21.6, then 24.1, and then it settles down to 22 and sits there for the rest of the table. Lower Manhattan delivers about 22 kilometers of street for every square kilometer of circle, no matter how big you draw the circle. That is what a grid does, and it is why buffers work fine here.

The crime density column bounces more than you might expect though. 6,631 per square kilometer at 200 meters, down to 3,577 at 400 meters, back up to 5,246 at 600. Nothing changed on the ground between those two numbers. That is entirely about which blocks happened to fall inside a circle of a particular radius, and it is the first hint that the measure is picking up geometry rather than crime.

# The same thing with network orders

Instead of a radius, expand over the network. Order 1 is the segment you start on. Order 2 is that segment plus everything sharing an intersection with it. Order 3 adds everything sharing an intersection with those, and so on. Because TIGER gives you the node ids, the whole thing is a breadth first search and the code is short:

    def network_orders(streets, seed, max_order):
        pairs, node2seg = build_graph(streets)
        cur = set(seed)
        out = [np.array(sorted(cur))]
        done_nodes = set()
        for _ in range(max_order - 1):
            front = set()
            for i in cur:
                front.update(pairs[i])
            new_nodes = front - done_nodes
            done_nodes |= front
            add = set()
            for n in new_nodes:
                add |= node2seg.get(n, set())
            cur = cur | add
            out.append(np.array(sorted(cur)))
        return out

The right hand panel of the map above shows the result, yellow at the seed grading out to purple at order 10.

|   Order |   Segments |   Street km |   Thefts |   Robberies |   Per street km |
|--------:|-----------:|------------:|---------:|------------:|----------------:|
|       1 |          1 |        0.09 |       31 |           2 |           383.8 |
|       2 |          6 |        0.48 |      201 |          30 |           481   |
|       3 |         20 |        1.52 |      287 |          38 |           213.7 |
|       4 |         46 |        3.8  |      832 |          61 |           235   |
|       5 |         77 |        6.68 |     1192 |          73 |           189.4 |
|       6 |        118 |       10.17 |     2808 |         119 |           287.9 |
|       7 |        172 |       14.97 |     4268 |         170 |           296.5 |
|       8 |        230 |       19.43 |     6447 |         216 |           342.9 |
|       9 |        294 |       24.7  |     7386 |         267 |           309.8 |
|      10 |        364 |       30.56 |     8344 |         336 |           284   |

That one block of Canal Street, 90 meters of it, carries 33 crimes over three years. The six segments at order 2 carry 231. There is no area denominator anywhere in this table, and there does not need to be one. You have a length, you have a count, and the ratio means something without any assumption about what is happening off the street.

I want to be honest that in Manhattan this is not a dramatic improvement. Both methods land in the same place. Crimes per street kilometer runs 200 to 300 either way you slice it:

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/Compare.png)

If Canal Street were the only case I looked at, the honest conclusion would be *use whichever one you like*. So let me go find a case where it matters.

# The Brooklyn Bridge

Same anchor logic, except the seed segment is a 570 meter span of the Brooklyn Bridge over the East River.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/BrooklynBridge_Map.png)

|   Meters |   Area |   % Land |   Street km |   Street km/sq km |   Thefts |   Robberies |   Per sq km |   Per street km |
|---------:|-------:|---------:|------------:|------------------:|---------:|------------:|------------:|----------------:|
|      100 |  0.031 |      0   |        0.4  |              12.7 |        0 |           0 |           0 |             0   |
|      200 |  0.125 |      0   |        0.8  |               6.4 |        0 |           0 |           0 |             0   |
|      300 |  0.282 |      1.4 |        1.2  |               4.2 |        0 |           0 |           0 |             0   |
|      400 |  0.502 |     19.7 |        4.04 |               8   |       56 |           4 |         120 |            14.9 |
|      500 |  0.784 |     34   |        7.64 |               9.7 |      138 |          14 |         194 |            19.9 |
|      600 |  1.129 |     42.4 |       13.46 |              11.9 |      373 |          38 |         364 |            30.5 |
|      700 |  1.537 |     49   |       20.9  |              13.6 |     1295 |          81 |         895 |            65.8 |
|      800 |  2.007 |     54.9 |       29.16 |              14.5 |     1726 |         117 |         918 |            63.2 |
|      900 |  2.541 |     59.3 |       39.12 |              15.4 |     2416 |         181 |        1022 |            66.4 |
|     1000 |  3.137 |     62.9 |       49.46 |              15.8 |     3881 |         252 |        1318 |            83.6 |

The `% Land` column is the whole post in one column. At 100 and 200 meters the buffer is zero percent land. Not *mostly* water, all of it, a circle drawn on the East River with a bridge deck running through the middle. Even at a full kilometer you are at 63% land.

Now read the crime density column next to it. Zero per square kilometer at 300 meters. If you handed that number to somebody without the map, they would tell you the middle of the Brooklyn Bridge is the safest place in New York City. It is not a crime rate. It is a statement about the East River.

And watch `Street km/sq km` do something Canal Street never did. It starts at 12.7, falls to 4.2 at 300 meters, then climbs back to 15.8 by a kilometer. That U shape is the artifact. The circle is growing as the square of the radius the entire time, but the amount of street inside it grows in fits and starts -- first just the bridge deck, then nothing new as the circle expands over open water, then a rush of street as it finally reaches land on both sides.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/Denominator.png)

Canal Street is the flat blue line in the middle panel. The Brooklyn Bridge is the brown one. Same city, same data, same method, and the denominator behaves completely differently. Any comparison you make between those two places using crime per square kilometer is comparing a property of their geometry, not a property of their crime.

The network orders have no such problem, because there is no area:

|   Order |   Segments |   Street km |   Thefts |   Robberies |   Per street km |
|--------:|-----------:|------------:|---------:|------------:|----------------:|
|       1 |          1 |        0.57 |        0 |           0 |             0   |
|       2 |          3 |        0.6  |        0 |           0 |             0   |
|       3 |          7 |        0.81 |        1 |           0 |             1.2 |
|       4 |         17 |        1.47 |        9 |           0 |             6.1 |
|       5 |         34 |        2.99 |       11 |           1 |             4   |
|       6 |         53 |        4.4  |       30 |           5 |             8   |
|       7 |         73 |        6.29 |       80 |           8 |            14   |
|       8 |        101 |        8.75 |      105 |          12 |            13.4 |
|       9 |        149 |       11.88 |      213 |          28 |            20.3 |
|      10 |        198 |       16.05 |      289 |          41 |            20.6 |

Orders 1 and 2 add almost nothing -- 570 meters of bridge, then 30 more meters. That is the network telling you something true, which is that a bridge is a bottleneck. It has two ends and no cross streets. A circle cannot express that. The network expansion does it for free, because a bottleneck in the real world is a low degree node in the graph.

# One thing I expected and did not get

I also computed shortest path distance along the network, and checked what share of the street length inside each buffer is genuinely within that distance on foot. I assumed the bridge would look terrible on this. It does not -- it runs 87 to 100%.

The reason is worth sitting with. The anchor is *on* the bridge, and the bridge is the thing that connects Manhattan to Brooklyn. Places across the river really are close to the middle of the span in travel terms. The buffer gets the right answer here, just for the wrong reason, and it pays for it by also swallowing a third of a square kilometer of river.

Canal Street is the one that loses street to unreachability, dropping from 90% at 100 meters to 81% at a kilometer. Even in a clean grid, about a fifth of what a circle grabs is further away than it looks, because you walk around blocks rather than through them.

So the barrier story I went in expecting is not the story the data told. The denominator story is.

# Caveats

A few things I would want a reviewer to push on.

**Network order is not a distance.** Order 10 at Canal Street reaches a median of 483 meters along the network. The same order 10 at the bridge reaches a median of 336 meters, because that seed is one long span with a cluster of short segments at each end. Order counts hops, not meters, and the exchange rate between the two is a property of the local network. Orders are comparable within a site and not across sites. If you need metric comparability, band by network distance instead -- the `net_dist` function in the repo gives you that, and it is a two line change.

**Segment length is not standardized.** TIGER edges split at intersections, which is what you want, but a long block and a short block are both one segment. Per kilometer handles this, per segment does not.

**Zero crimes on the bridge span is probably a geocoding artifact.** NYPD complaints get addresses, and an incident on the walkway very likely lands at whichever entrance the report was taken. So the vending enforcement that prompted me to pick this site would not show up on the span at all. That is a good reminder that a street unit analysis inherits whatever the geocoder did.

**Three years of larceny in lower Manhattan is a lot of crime.** These counts are large enough that none of the patterns above are small sample noise. Try the same exercise on robberies alone in a smaller city and the order 1 and 2 rows get very thin very fast.

# What I would actually do

Buffers are not wrong. They are a measurement instrument with a known failure mode, and the failure mode is that they assume area is a reasonable proxy for opportunity. In a dense uniform grid it is, which is why Canal Street came out the same either way.

The check is cheap. Clip the network to your buffer and divide street length by area. If that ratio is stable across the radii you care about, use the buffer, it is one click and everybody understands it. If it swings the way it does at the Brooklyn Bridge, the buffer is measuring your geography instead of your crime, and you want a street network measure instead.

This matters most for exactly the cases people care about -- waterfronts, parks, highways, rail corridors, big box parking lots, anywhere the built environment is not a grid. Those are also the places where somebody is most likely to be arguing about a distance in an ordinance.

If you want more on the underlying spatial statistics, I have written about [the spatial point pattern test](https://crimede-coder.com/blogposts/2025/SPPT) for comparing crime distributions over time, and about [identifying high return hot spots](https://andrewpwheeler.com/2020/10/08/recent-papers-on-hot-spots-of-crime-in-dallas/). The geopandas and network code here is the kind of thing I cover in [my data science book](https://crimede-coder.com/blogposts/2024/PythonDataScience).
