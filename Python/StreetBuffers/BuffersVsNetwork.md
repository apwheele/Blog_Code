<!---
Fixed width buffers versus street network measures
-->

*AI disclosure -- this post was created via Claude Code using Claude Opus 5. I gave it the idea, the two study sites and my prior blog posts as style examples, and it wrote the code and the draft. I will always disclose when I use AI to heavily write any content on this blog. (I use it for minor copy editing all the time.)*

Buffers are the default way analysts define the area around a place. You have a bar, a bus stop, a stretch of street, and you want to know how much crime is nearby, so you draw a fixed width band around it. Everybody does it and for most questions it is fine.

Here is the problem. A buffer divides by *area*, and area is not what generates crime. Streets are. When the ratio of street to area is stable, buffers work. When it is not, the buffer gives you a number that looks like a crime rate but is really a statement about your geometry.

I use two runs of street in New York City. Canal Street at Broadway, the counterfeit goods market, which sits in a clean grid. And the span of the Brooklyn Bridge over the East River, which sits in a river. [Data and code are on github](https://github.com/apwheele/Blog_Code/tree/master/Python/StreetBuffers).

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

# Buffers along Canal Street

Buffers every 100 meters out from the street itself, out to a kilometer.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/CanalSt_Map.png)

|   Meters |   Area |   % Land |   Street km |   Street km/sq km |   Thefts |   Robberies |   Per sq km |   Per street km |
|---------:|-------:|---------:|------------:|------------------:|---------:|------------:|------------:|----------------:|
|      100 |  0.2   |    100   |        4.61 |              23   |      652 |          68 |        3594 |           156.3 |
|      200 |  0.463 |    100   |       10.69 |              23.1 |     1490 |         104 |        3440 |           149.1 |
|      300 |  0.789 |    100   |       17.99 |              22.8 |     2343 |         163 |        3176 |           139.3 |
|      400 |  1.178 |    100   |       26.98 |              22.9 |     4442 |         278 |        4008 |           174.9 |
|      500 |  1.629 |    100   |       37.88 |              23.3 |     5360 |         357 |        3510 |           150.9 |
|      600 |  2.143 |    100   |       49.28 |              23   |     9068 |         456 |        4445 |           193.3 |
|      700 |  2.719 |     99.7 |       61.28 |              22.5 |    10374 |         548 |        4017 |           178.2 |
|      800 |  3.358 |     97.9 |       72.78 |              21.7 |    13065 |         688 |        4095 |           189   |
|      900 |  4.06  |     95.6 |       86.25 |              21.2 |    16419 |         853 |        4254 |           200.3 |
|     1000 |  4.825 |     92.5 |       99.68 |              20.7 |    20618 |         979 |        4476 |           216.7 |

Look at `Street km/sq km`. It is 23 at 100 meters and 20.7 at a kilometer. Lower Manhattan hands you about 22 kilometers of street for every square kilometer you enclose, no matter how wide the band. That is what a grid does, and it is why buffers are fine here. Crimes per square kilometer runs 3,176 to 4,476 across the whole table.

# The same thing with network orders

Instead of a width, expand over the network. Order 1 is the street you started on. Order 2 is that plus everything sharing an intersection with it. Order 3 adds everything sharing an intersection with those, and so on. TIGER gives you the node ids, so it is a breadth first search:

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

|   Order |   Segments |   Street km |   Thefts |   Robberies |   Per street km |
|--------:|-----------:|------------:|---------:|------------:|----------------:|
|       1 |         12 |        0.84 |      197 |          25 |           262.8 |
|       2 |         36 |        3.2  |      535 |          56 |           184.5 |
|       3 |         86 |        7.62 |     1436 |          95 |           201   |
|       4 |        147 |       12.65 |     2123 |         136 |           178.6 |
|       5 |        213 |       17.92 |     4020 |         191 |           234.9 |
|       6 |        276 |       23.05 |     5401 |         253 |           245.3 |
|       7 |        355 |       29.9  |     7845 |         331 |           273.5 |
|       8 |        442 |       37.29 |     9816 |         422 |           274.6 |
|       9 |        541 |       44.69 |    11244 |         515 |           263.1 |
|      10 |        652 |       53.46 |    12316 |         574 |           241.1 |

That 845 meters of Canal Street carries 222 crimes over three years. There is no area denominator anywhere in this table and there does not need to be one. You have a length and a count.

In Manhattan the two methods agree, which is the honest result. If Canal Street were the only site I looked at, the conclusion would be use whichever you like.

# The Brooklyn Bridge

Same code, seeded on the span over the river.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/BrooklynBridge_Map.png)

|   Meters |   Area |   % Land |   Street km |   Street km/sq km |   Thefts |   Robberies |   Per sq km |   Per street km |
|---------:|-------:|---------:|------------:|------------------:|---------:|------------:|------------:|----------------:|
|      100 |  0.187 |     32.1 |        3.3  |              17.7 |       33 |           3 |         193 |            10.9 |
|      200 |  0.428 |     40.9 |        6.15 |              14.4 |      114 |           5 |         278 |            19.3 |
|      300 |  0.731 |     49.2 |       10.19 |              13.9 |      245 |          28 |         373 |            26.8 |
|      400 |  1.097 |     55.8 |       15.79 |              14.4 |      483 |          54 |         489 |            34   |
|      500 |  1.526 |     59.2 |       24.25 |              15.9 |     1397 |          93 |         976 |            61.4 |
|      600 |  2.018 |     62.5 |       33.47 |              16.6 |     1932 |         133 |        1023 |            61.7 |
|      700 |  2.572 |     65.8 |       43.71 |              17   |     2660 |         221 |        1120 |            65.9 |
|      800 |  3.189 |     68.4 |       54.54 |              17.1 |     4095 |         275 |        1370 |            80.1 |
|      900 |  3.869 |     70.4 |       66.33 |              17.1 |     5827 |         366 |        1601 |            93.4 |
|     1000 |  4.612 |     71.9 |       79.13 |              17.2 |     7482 |         468 |        1724 |           100.5 |

At 100 meters the buffer is 32% land. The rest is the East River. And now watch crimes per square kilometer: 193 at 100 meters, 1,724 at a kilometer. Nine times higher, for the same piece of bridge. Nothing about the bridge changed, the buffer just grew until it reached land on both sides.

`Street km/sq km` shows the same thing from the other side. It falls from 17.7 to 13.9 and then climbs back to 17.2. Canal Street never does that.

![](https://raw.githubusercontent.com/apwheele/Blog_Code/master/Python/StreetBuffers/Denominator.png)

Canal Street is blue, the bridge is brown. Any comparison you make between those two places using crime per square kilometer is comparing their geometry, not their crime.

The network orders have no such problem, because there is no area:

|   Order |   Segments |   Street km |   Thefts |   Robberies |   Per street km |
|--------:|-----------:|------------:|---------:|------------:|----------------:|
|       1 |          6 |        1.33 |        0 |           0 |             0   |
|       2 |         15 |        1.81 |        1 |           1 |             1.1 |
|       3 |         30 |        2.82 |       15 |           2 |             6   |
|       4 |         48 |        4.03 |       54 |           2 |            13.9 |
|       5 |         68 |        5.94 |       85 |           8 |            15.7 |
|       6 |        101 |        8.24 |      181 |          26 |            25.1 |
|       7 |        141 |       11.71 |      212 |          29 |            20.6 |
|       8 |        194 |       15.16 |      250 |          36 |            18.9 |
|       9 |        254 |       20.02 |      355 |          50 |            20.2 |
|      10 |        320 |       25.12 |      527 |          65 |            23.6 |

Orders 1 and 2 add almost nothing, 1.33 kilometers of bridge and then 480 more meters. That is the network telling you a bridge is a bottleneck, it has two ends and no cross streets. A band of fixed width cannot express that, a graph does it for free.

# Caveats

Network order is not a distance. Order 10 reaches a median of 430 meters along the network at Canal Street and 392 meters at the bridge, and that exchange rate is a property of the local network. Orders are comparable within a site, not across sites. If you need metric comparability, band by network distance instead, which is the `net_dist` function in the repo.

The zero crimes on the bridge span is very likely a geocoding artifact. NYPD complaints get addresses, and an incident on the walkway probably lands at whichever entrance took the report. A street unit analysis inherits whatever the geocoder did.

# What I would actually do

Buffers are not wrong, they just assume area is a reasonable proxy for opportunity. In a dense uniform grid it is, which is why Canal Street came out the same either way.

The check is cheap. Clip the street network to your buffer and divide street length by area. If that ratio is stable across the widths you care about, use the buffer, it is one click and everybody understands it. If it swings the way it does at the bridge, use a street network measure.

This matters most at waterfronts, parks, highways, rail corridors and big parking lots -- anywhere the built environment is not a grid. Those are also the places where somebody is most likely to be arguing about a distance in an ordinance.

If you want more on the underlying spatial statistics, I have written about [the spatial point pattern test](https://crimede-coder.com/blogposts/2025/SPPT) for comparing crime distributions over time, and about [identifying high return hot spots](https://andrewpwheeler.com/2020/10/08/recent-papers-on-hot-spots-of-crime-in-dallas/).
