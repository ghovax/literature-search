# Corpus shape: counts instead of a list

When the question is "how much / when / where" rather than "which papers".

OpenAlex only, because faceting is its feature: `https://api.openalex.org/works?search=<q>&group_by=<field>&mailto=<you>`

`<field>` is one of: `publication_year`, `authorships.institutions.id`, `primary_location.source.id`, `type`, `open_access.oa_status`, `primary_topic.id`, `authorships.countries`.

Restrict the population with the usual filters (`filter=from_publication_date:...`). Results come as `{key, key_display_name, count}`, already sorted by count — that *is* the histogram or top-N.

**State that these counts are OpenAlex-only.** Other databases are not aggregated, so this describes one index's view, not the literature.
