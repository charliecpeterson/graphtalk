### A. Claude in Excel (`bike_data.xlsx`)

```text
What is on each tab? One line each.
```

```text
Which was the busiest day in daily_summary, and what is odd about it?
```

```text
Compare member and casual trips by day of week. Put a chart on a new tab.
```

```text
How much do trips fall as the temperature drops? Chart it and tell me the number.
```

```text
Add a weekday/weekend column and show how the rider mix differs between them.
```

### B. Claude Code, skill 1: dashboard-export

```text
/dashboard-export Build a dashboard of data/bikeshare and publish it as an artifact. Answer five questions, one plot each, in this order:
1. Who rides when? Average trips by hour and weekday, members versus casual riders.
2. How does weather change riding? Trips per day against temperature and rain.
3. Which days stand out? A calendar of the year that marks the biggest days.
4. Did e-bikes gain share? E-bike share by neighborhood, first half of the year versus second half, and the city total.
5. Where do bikes pile up? Net flow by station: which stations fill and which drain.
Pick the chart form that fits each question. Skip plain bar, pie and scatter charts unless one is truly the best choice. Then do what the skill says: save the files in out/ and look at the page and every plot file before you tell me it is done.
```

```text
If it plays safe, name the forms: an hour-by-weekday heatmap; a calendar heatmap
that marks the biggest days; small multiples by neighborhood; a dumbbell of e-bike
share, first half versus second half, by neighborhood; net bike flow by station.
```

```text
Open the dashboard and every plot file, look at them, and fix what is wrong.
```

### C. Claude Code, skill 2: template-charlie

```text
/template-charlie /dashboard-export Redo the same five-question dashboard of data/bikeshare in my style and publish it as an artifact. Every number in a headline or margin note must be computed from the data. Save the files in out/, then look at the page and every plot file and fix what is wrong.
```

```text
/template-charlie Redraw the e-bike figure. Every number in the margin notes
must be computed from the data.
```

### D. Live edit (on a copy)

```text
Copy data/bikeshare/trips.csv to trips_edited.csv, drop every trip that starts or
ends at Harbor Flats, and redraw the e-bike figure from the edited file.
```

### E. With and without the style skill (slide "Same facts, two looks")

```text
Using data/bikeshare/trips.csv, did the e-bike share of trips change between the first and second half of 2025? Compare each starting neighborhood and the whole city. If the neighborhoods and the city disagree, show why. Make one figure for a slide.
```

Run it once without `template-charlie` installed, and once with `/template-charlie` at the front.
