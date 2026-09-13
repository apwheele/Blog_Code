# Buffers vs street network measures

Code for the blog post [Fixed width buffers versus street network measures](BuffersVsNetwork.md).

Compares fixed width circular buffers against street network expansion for two
sites in New York City, Canal St at Broadway (dense grid) and the middle of the
Brooklyn Bridge (mostly river). Point of the post is that a buffer divides by
area, and area is only a reasonable proxy for criminal opportunity when the
ratio of street to area is stable.

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
