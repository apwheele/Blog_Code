<!---
Using DuckDB WASM + Cloudflare R2 to host and query big data (for almost free)
-->

The motivation here, prompted by a recent question [Abigail Haddad](https://www.linkedin.com/posts/abigail-haddad_ive-got-150-million-rows-of-data-zero-budget-activity-7343303464350806030-j5uh?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAox8IkBbf2Iqpg0sDyNtFHv0Z1JRHUm0QE) had on LinkedIn:

![](https://lh3.googleusercontent.com/pw/AP1GczNB_Gf4qwPo7DJDwnKOnZIkAtNMOAqHX-0vw61Nn0xsksHLHpXN7Wxb-mLit8RcAefaI1HyUMEoO-Pm3oodXCQIFXQmUMCWl5-_uAYXcLkEifntD9QpPcRiFT-wIPDq7uxB90djjW6kbNYLOuv71cN9=w803-h607-s-no-gm?authuser=0)

For the machines, the context is hosting a dataset of 150 million rows (in another post Abigail stated it was around 72 gigs). And you want the public to be able to make ad-hoc queries on that data. Examples where you may want to do this are public dashboards (think a cities open data site, just puts all the data on R2 and has a front end).

This is the point where traditional SQL databases for websites probably don't make sense. Databases like [Supabase Postgres](https://andrewpwheeler.com/2023/06/19/some-adventures-in-cloud-computing/) or MySQL can have that much data, given the cost of cloud computing though and what they are typically used for, it does not make much sense to put 72 gigs and use them for data analysis type queries.

Hosting the data as static files though in an online bucket, like [Cloudflare's R2](https://developers.cloudflare.com/r2/pricing/), and then querying the data makes more sense for that size. Here to query the data, I also use a [WASM deployed DuckDB](https://duckdb.org/docs/stable/clients/wasm/overview.html). What this means is I don't really have to worry about a server at all -- it should scale to however many people want to use the service (I am just serving up HTML). The client's machine handles creating the query and displaying the resulting data via javascript, and Cloudflare basically just pushes data around.

If you want to see it in action, you can check out the [github repo](https://github.com/apwheele/apwheele.github.io/tree/master/MathPosts/DuckDB), or see the [demo deployed on github pages](https://apwheele.github.io/MathPosts/DuckDB/index.html) to illustrate generating queries. To check out a query on my Cloudflare R2 bucket, you can run `SELECT * FROM 'https://data-crimedecoder.com/books.parquet' LIMIT 10;`:

![](https://lh3.googleusercontent.com/pw/AP1GczM9rxqu7xqbggnFD-toED-Cex2HxEdvrr6XWD9kCv5h--xUI9Rc3TkgPnM8SbvgajMUaIdf-9aNTKTlUq9H9xWPnWfRs3V93yQQklKtXqV8Mja_Hte3q7SBfKJC0t_ejf_A-GIwEKSHPzwf9SibeV_7=w1676-h790-s-no-gm?authuser=0)

Cloudflare is nice here, since there is no egress charges (big data you need to worry about that). You do get charged for different read/write operations, but the free tiers seem quite generous (I do not know quite how to map these queries to Class B operations in Cloudflare's parlance, but you get 10 million per month and all my tests only generated a few thousand).

For some notes on this set-up. On Cloudflare, to be able to use DuckDB WASM, I needed expose the R2 bucket via a custom domain. Using the development url did not work (same [issue as here](https://github.com/duckdb/duckdb-wasm/discussions/1718)). I also set my CORS Policy to:

    [
      {
        "AllowedOrigins": [
          "*"
        ],
        "AllowedMethods": [
          "GET",
          "HEAD"
        ],
        "AllowedHeaders": [
          "*"
        ],
        "ExposeHeaders": [],
        "MaxAgeSeconds": 3000
      }
    ]


While my Crime De-Coder site is PHP, all the good stuff happens client-side. So you can see some example demo's of the [GSU book prices data](https://crimede-coder.com/graphs/GSUBooksQuery).

![](https://www.crimede-coder.com/images/GSU_BookDashboard.png)

One of the annoying things about this though, with S3 you can partition the files and [query multiple partitions at once](https://andrewpwheeler.com/2023/08/14/querying-osm-places-data-in-python/). Here something like `SELECT * FROM read_parquet('https://data-crimedecoder.com/parquet/Semester=*/*') LIMIT 10;` does not work. You can union the partitions together manually. So not sure if there is a way to set up R2 to work the same way as the S3 example (set up a FTP server? let me know in the comments!). 

![](https://lh3.googleusercontent.com/pw/AP1GczOUpT1UhKSdZxN35h9CUaQjo5XnfqkTAvYtDbC1yQoqB5iSXLn_fzBRl6LWcxWIaFF2oh0n-j0jhX71MGz8_-h4LArGko3IZ81Fz4zajtkLF8jppUmhOoE1Tz0ENz1Vyq7l0h5vHweo3YufRuLGsqtA=w1562-h743-s-no-gm?authuser=0)

For pricing, for the scenario Abigail had of 72 gigs of data, we then have:

 - $10 per year for the domain
 - `0.015*72*12 = $13` for storage of the 72 gigs 

So we have a total cost to run this of $23 per year. And it can scale to a crazy number of users and very large datasets out of the box. (My usecase here is just $10 for the domain, you get 10 gigs for free.)

Since this can be deployed on a static site, there are free options (like github pages). So the page with the SQL query part is essentially free. (I am not sure if there is a way to double dip on the R2 custom domain, such as just putting the HTML in the bucket.)

While this example only shows generating a table, you can do whatever additional graphics client side. So could make a normal looking dashboard with dropdowns, and those just execute various queries and fill in the graphs/tables.