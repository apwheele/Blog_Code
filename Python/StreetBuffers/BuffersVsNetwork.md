<!---
Fixed width buffers versus street network measures
-->

*AI disclosure -- this post was created via Claude Code using Claude Opus 5. I gave it the idea, the two study sites and my prior blog posts as style examples, and it wrote the code and the draft. I will always disclose when I use AI to heavily write any content on this blog. (I use it for minor copy editing all the time.)*

Buffers are the default way analysts define the area around a place. You have a bar, a bus stop, a stretch of street, and you want to know how much crime is nearby, so you draw a fixed width band around it. Everybody does it and for most questions it is fine.

Here is the problem. A buffer divides by *area*, and area is not what generates crime. Streets are. When the ratio of street to area is stable, buffers work. When it is not, the buffer gives you a number that looks like a crime rate but is really a statement about your geometry.

I use two runs of street in New York City. Canal Street at Broadway, the counterfeit goods market, which sits in a clean grid. And the span of the Brooklyn Bridge over the East River, which sits in a river. [Data and code are on github](https://github.com/apwheele/Blog_Code/tree/master/Python/StreetBuffers).

Everything below is in exclusive bands. The 100-200 row is the ring between 100 and 200 meters out, not the whole disk, so each crime is counted once. Cumulative buffers hide most of what I am about to show, since every ring inherits the ones inside it.

# The setup

Three years of NYPD complaint data, 2023 through 2025, thefts (petit and grand larceny) and robberies from the NYC open data Socrata endpoint. 49,270 thefts and 2,558 robberies in the bounding box.

For streets I use `pygris`, Kyle Walker's `tigris` ported to python:

    uv init
    uv add geopandas pygris networkx matplotlib requests

One thing to know. `pygris.roads()` returns whole named streets, so Canal St comes back as three features, the longest running 2.1 kilometers with no intersections in it. You cannot expand a network over that. You want TIGER **edges**, which are split at every intersection and carry `TNIDF` and `TNIDT` node ids, so the topology is already in the file. `pygris` does not expose an `edges()` function but its loader takes the url:

    from pygris.helpers import _load_tiger

    url = 'https://www2.census.gov/geo/tiger/TIGER2023/EDGES/tl_2023_36061_edges.zip'
    e = _load_tiger(url, cache=True)
    e = e[(e['ROADFLG'] == 'Y') & (e['MTFCC'].isin(KEEP))]

Same street, 40 edges instead of 3. That leaves 6,816 segments across Manhattan and Brooklyn after filtering to travel ways and clipping to the study area. Everything is projected to UTM 18N so units are meters, and crimes snap to their nearest segment within 50 meters, which catches 99.0% of them.

Both study sites are a run of street, not a point. Canal St is the twelve segments within 400 meters of Broadway, 845 meters of street. The bridge is the six segments TIGER names `Brooklyn Brg` that cross water, 1,327 meters, 86% of which is over the river.

# Buffer bands along Canal Street

Bands every 100 meters out from the street itself, out to a kilometer.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/CanalSt_Map.png)

| Band (m)   |   Area |   % Land |   Street km |   Street km/sq km |   Thefts |   Robberies |   Per sq km |   Per street km |   % reachable |
|:-----------|-------:|---------:|------------:|------------------:|---------:|------------:|------------:|----------------:|--------------:|
| 0-100      |  0.2   |    100   |        4.61 |              23   |      652 |          68 |        3594 |           156.3 |          95.2 |
| 100-200    |  0.263 |    100   |        6.08 |              23.1 |      838 |          36 |        3323 |           143.6 |          85.9 |
| 200-300    |  0.326 |    100   |        7.3  |              22.4 |      853 |          59 |        2800 |           124.9 |          78.2 |
| 300-400    |  0.388 |    100   |        8.99 |              23.1 |     2099 |         115 |        5699 |           246.2 |          67   |
| 400-500    |  0.451 |    100   |       10.9  |              24.2 |      918 |          79 |        2210 |            91.5 |          63.7 |
| 500-600    |  0.514 |    100   |       11.4  |              22.2 |     3708 |          99 |        7408 |           334.1 |          53.4 |
| 600-700    |  0.577 |     98.4 |       12.01 |              20.8 |     1306 |          92 |        2425 |           116.4 |          44.6 |
| 700-800    |  0.639 |     90.4 |       11.5  |              18   |     2691 |         140 |        4429 |           246.2 |          44.4 |
| 800-900    |  0.702 |     84.5 |       13.47 |              19.2 |     3354 |         165 |        5013 |           261.2 |          36.8 |
| 900-1000   |  0.765 |     76   |       13.43 |              17.6 |     4199 |         126 |        5656 |           322.1 |          37.8 |

The street supply is steady. `Street km/sq km` sits at 22 to 24 for the first six bands, which is what a grid does, and only sags at the end when the outer rings start hitting the Hudson and the East River.

The crime density is not steady at all. 2,210 per square kilometer in the 400-500 band, 7,408 in the very next one. That is a factor of three between adjacent rings, and nothing about Canal Street changed in those hundred meters. What changed is that the 500-600 ring happens to catch a stretch of Broadway and the blocks around it. Ring geometry is picking which hot blocks you get.

The last column is worth a look too. `% reachable` is the share of street in the band that is genuinely within that distance by shortest path on the network rather than as the crow flies. It starts at 95% and falls to 38%. Even in a clean grid, most of what the outer rings grab is further away on foot than the ring says, because you walk around blocks instead of through them.

# The same thing with network orders

Instead of a width, expand over the network. Order 1 is the street you started on. Order 2 is the segments that share an intersection with it. Order 3 is the segments that share an intersection with those, and so on. Each row below is only the segments first reached at that order. TIGER gives you the node ids, so it is a breadth first search:

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

The right panel above shows it, yellow at the seed grading out to purple at order 10.

|   Order |   New segs |   Street km |   Thefts |   Robberies |   Per street km |
|--------:|-----------:|------------:|---------:|------------:|----------------:|
|       1 |         12 |        0.84 |      197 |          25 |           262.8 |
|       2 |         24 |        2.36 |      338 |          31 |           156.5 |
|       3 |         50 |        4.42 |      901 |          39 |           212.9 |
|       4 |         61 |        5.03 |      687 |          41 |           144.6 |
|       5 |         66 |        5.27 |     1897 |          55 |           370.2 |
|       6 |         63 |        5.12 |     1381 |          62 |           281.6 |
|       7 |         79 |        6.85 |     2444 |          78 |           368.2 |
|       8 |         87 |        7.39 |     1971 |          91 |           279.1 |
|       9 |         99 |        7.41 |     1428 |          93 |           205.4 |
|      10 |        111 |        8.77 |     1072 |          59 |           129   |

That 845 meters of Canal Street carries 222 crimes over three years. There is no area denominator anywhere in this table and there does not need to be one. You have a length and a count.

Per street kilometer still moves around, because some orders reach busier blocks than others. The difference is that the denominator is a thing that exists rather than a circle you drew.

# The Brooklyn Bridge

Same code, seeded on the span over the river.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/BrooklynBridge_Map.png)

| Band (m)   |   Area |   % Land |   Street km |   Street km/sq km |   Thefts |   Robberies |   Per sq km |   Per street km |   % reachable |
|:-----------|-------:|---------:|------------:|------------------:|---------:|------------:|------------:|----------------:|--------------:|
| 0-100      |  0.187 |     32.1 |        3.3  |              17.7 |       33 |           3 |         193 |            10.9 |          90.7 |
| 100-200    |  0.241 |     47.8 |        2.85 |              11.9 |       81 |           2 |         345 |            29.1 |          75.3 |
| 200-300    |  0.304 |     60.7 |        4.03 |              13.3 |      131 |          23 |         507 |            38.2 |          61.2 |
| 300-400    |  0.366 |     69.1 |        5.61 |              15.3 |      238 |          26 |         721 |            47.1 |          53.9 |
| 400-500    |  0.429 |     67.9 |        8.46 |              19.7 |      914 |          39 |        2222 |           112.7 |          43.2 |
| 500-600    |  0.492 |     72.5 |        9.22 |              18.7 |      535 |          40 |        1170 |            62.4 |          37.8 |
| 600-700    |  0.554 |     77.9 |       10.24 |              18.5 |      728 |          88 |        1472 |            79.7 |          36.5 |
| 700-800    |  0.617 |     79.1 |       10.83 |              17.6 |     1435 |          54 |        2413 |           137.4 |          28.8 |
| 800-900    |  0.68  |     80   |       11.79 |              17.3 |     1732 |          91 |        2682 |           154.7 |          21.6 |
| 900-1000   |  0.743 |     79.7 |       12.8  |              17.2 |     1655 |         102 |        2366 |           137.2 |          27.1 |

Compare the first two rows. The 100-200 ring has 29% more area than the 0-100 ring and 14% *less* street in it, because that second ring is almost entirely open water. In a grid, a bigger ring always means more street. Here it does not, and that is the whole problem in two rows.

The 0-100 band is 32% land. Crime density climbs from 193 per square kilometer to 2,682, a factor of fourteen, purely as the rings work their way off the river and onto land.

`% reachable` gets worse than Canal Street, down to 22% in the 800-900 band. Four fifths of the street that ring grabs is not actually 800 to 900 meters from the bridge on foot.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/Denominator.png)

Canal Street is blue, the bridge is brown. The middle panel is the one that matters -- Canal is flat in the twenties until the river, the bridge dives to 12 and climbs back. Any comparison between those two places using crime per square kilometer is comparing their geometry, not their crime.

The network orders have no such problem, because there is no area:

|   Order |   New segs |   Street km |   Thefts |   Robberies |   Per street km |
|--------:|-----------:|------------:|---------:|------------:|----------------:|
|       1 |          6 |        1.33 |        0 |           0 |             0   |
|       2 |          9 |        0.48 |        1 |           1 |             4.1 |
|       3 |         15 |        1.01 |       14 |           1 |            14.8 |
|       4 |         18 |        1.21 |       39 |           0 |            32.3 |
|       5 |         20 |        1.91 |       31 |           6 |            19.4 |
|       6 |         33 |        2.3  |       96 |          18 |            49.5 |
|       7 |         40 |        3.47 |       31 |           3 |             9.8 |
|       8 |         53 |        3.45 |       38 |           7 |            13.1 |
|       9 |         60 |        4.86 |      105 |          14 |            24.5 |
|      10 |         66 |        5.1  |      172 |          15 |            36.6 |

Order 2 adds nine segments and 480 meters. Order 2 at Canal Street adds twenty four segments and 2.4 kilometers. That is the network telling you a bridge is a bottleneck, it has two ends and no cross streets. A band of fixed width cannot express that, a graph does it for free.

# Caveats

Network order is not a distance. Order 10 reaches a median of 430 meters along the network at Canal Street and 392 meters at the bridge, and that exchange rate is a property of the local network. Orders are comparable within a site, not across sites. If you need metric comparability, band by network distance instead, which is the `net_dist` function in the repo.

The zero crimes on the bridge span is very likely a geocoding artifact. NYPD complaints get addresses, and an incident on the walkway probably lands at whichever entrance took the report. A street unit analysis inherits whatever the geocoder did.

# What I would actually do

Buffers are not wrong, they just assume area is a reasonable proxy for opportunity. In a dense uniform grid it mostly is, which is why Canal Street's street supply held steady.

The check is cheap. Clip the street network to your bands and divide street length by area. If that ratio is stable across the widths you care about, a buffer is fine, it is one click and everybody understands it. If it moves the way it does at the bridge, use a street network measure.

This matters most at waterfronts, parks, highways, rail corridors and big parking lots -- anywhere the built environment is not a grid. Those are also the places where somebody is most likely to be arguing about a distance in an ordinance.

If you want more on the underlying spatial statistics, I have written about [the spatial point pattern test](https://crimede-coder.com/blogposts/2025/SPPT) for comparing crime distributions over time, and about [identifying high return hot spots](https://andrewpwheeler.com/2020/10/08/recent-papers-on-hot-spots-of-crime-in-dallas/).
