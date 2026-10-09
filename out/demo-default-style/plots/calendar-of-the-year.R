# plots/calendar-of-the-year.R: run from out/<slug>/
library(ggplot2); library(readr)

# Edit here ---------------------------------------------------------------
title    <- "The ten biggest days are all weekends in summer and early autumn"
subtitle <- "Trips per day, 2025. Outlined cells are the ten busiest days, numbered by rank."
col_low  <- "#cde2fb"; col_high <- "#0d366b"; col_mark <- "#eb6834"
# -------------------------------------------------------------------------

d <- read_csv("data/calendar-of-the-year.csv", show_col_types = FALSE)
d$weekday <- factor(d$weekday, rev(c("Mon","Tue","Wed","Thu","Fri","Sat","Sun")))
top <- d[d$top10, ]; top$lab <- sprintf("%d  %s %d: %d trips", top$rank, top$month, as.integer(format(top$date, "%d")), top$trips)
top <- top[order(top$rank), ]; top$y <- seq(6.5, by = -0.62, length.out = nrow(top))
mon <- aggregate(week ~ month, d, min); mon$month <- factor(mon$month, month.abb)

p <- ggplot(d, aes(week, weekday)) +
  geom_tile(aes(fill = trips), colour = "#fcfcfb", linewidth = 0.5) +
  geom_tile(data = top, fill = NA, colour = col_mark, linewidth = 0.9) +
  geom_text(data = top, aes(label = rank), size = 2.4, colour = "white", fontface = "bold") +
  geom_text(data = mon, aes(week, 7.9, label = month), hjust = 0, size = 3, colour = "#52514e", inherit.aes = FALSE) +
  geom_text(data = top, aes(55.5, y, label = lab), hjust = 0, size = 3, colour = "#0b0b0b", inherit.aes = FALSE) +
  scale_fill_gradient(low = col_low, high = col_high, name = "Trips") +
  scale_x_continuous(expand = expansion(add = c(0.5, 0)), limits = c(-0.5, 66)) +
  coord_cartesian(clip = "off", ylim = c(0.5, 7.9)) +
  labs(title = title, subtitle = subtitle, x = NULL, y = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid = element_blank(), axis.text.x = element_blank(), plot.title = element_text(face = "bold"),
        plot.background = element_rect(fill = "#fcfcfb", colour = NA))

ggsave("plots/calendar-of-the-year.svg", p, width = 10, height = 3.6)
ggsave("plots/calendar-of-the-year.png", p, width = 10, height = 3.6, dpi = 200)
