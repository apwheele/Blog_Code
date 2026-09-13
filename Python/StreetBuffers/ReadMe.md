# Buffers vs street network measures

Code for the blog post [Fixed width buffers versus street network measures](BuffersVsNetwork.md).

Compares fixed width buffers against street network expansion for two runs of
street in New York City, Canal St at Broadway (dense grid) and the span of the
Brooklyn Bridge over the East River. Point of the post is that a buffer divides
by area, and area is only a reasonable proxy for criminal opportunity when the
ratio of street to area is stable.

All measures are **exclusive bands**, not cumulative. The 100-200 buffer row is
the ring between 100 and 200 meters out, and network order 3 is only the
segments first reached at that order, so a crime is counted once.

Both sites are a line, not a point. Buffers are taken out from the street
itself, and the network seed is the same set of segments. Canal St is the 12
segments within 400m of Broadway (845m of street), the bridge is the 6 segments
named `Brooklyn Brg` that cross water (1,327m, 86% of it over the river).

## Running it

Needs [uv](https://docs.astral.sh/uv/).

    uv sync
    uv run GetData.py     # downloads crime data and TIGER edges
    uv run Analysis.py    # tables, csvs and figures
    uv run MakeTables.py  # markdown tables for the post
    uv run MakeHTML.py    # BuffersVsNetwork.html

`GetData.py` hits the network, the rest run off the local files it writes.

## Files

| File | What it does |
|---|---|
| `GetData.py` | NYPD complaints from NYC open data, TIGER edges and area water via pygris |
| `StreetNet.py` | Graph building, network order expansion, shortest path distance, the buffer and network tables |
| `Analysis.py` | Runs both sites, writes the csvs and the figures |
| `MakeTables.py` | Formats the result csvs as markdown |
| `MakeHTML.py` | Markdown to standalone html |
| `cdcplot.py` | My matplotlib theme, copied from `../LinePlots` |

## Data notes

Crime is NYPD complaint data, 2023 through 2025, petit and grand larceny plus
robbery, inside a bounding box covering lower Manhattan and the Brooklyn Bridge.
49,270 thefts and 2,558 robberies.

Streets are TIGER/Line **edges**, not `pygris.roads()`. Edges are split at every
intersection and carry `TNIDF`/`TNIDT` node ids, which is what makes the network
expansion work. `roads()` returns whole named streets, so Canal St comes back as
three features rather than 40 and there is nothing to traverse. `pygris` does not
expose an `edges()` function, so `GetData.py` calls `pygris.helpers._load_tiger`
on the EDGES url directly.

Everything is projected to UTM 18N (EPSG:32618) so units are meters. Crimes snap
to their nearest segment within 50m, which catches 99.0% of them.

Sites are configured in the `SITES` dict at the top of `Analysis.py`. Pass
`within` to trim a named street to a radius around a point, or `over_water` to
keep only the segments crossing water.
