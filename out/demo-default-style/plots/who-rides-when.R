# plots/who-rides-when.R: run from out/<slug>/
library(ggplot2); library(readr)

# Edit here ---------------------------------------------------------------
title    <- "Members ride the commute; casual riders ride weekend afternoons"
subtitle <- "Average trips per hour slot, by weekday and hour of day, 2025 (same color scale in both panels)"
col_low  <- "#cde2fb"; col_high <- "#0d366b"
# -------------------------------------------------------------------------

d <- read_csv("data/who-rides-when.csv", show_col_types = FALSE)
d$weekday <- factor(d$weekday, rev(c("Mon","Tue","Wed","Thu","Fri","Sat","Sun")))
d$rider_type <- factor(d$rider_type, c("member", "casual"), c("Members", "Casual riders"))

p <- ggplot(d, aes(hour, weekday, fill = avg_trips)) +
  geom_tile(colour = "#fcfcfb", linewidth = 0.4) +
  facet_wrap(~rider_type, ncol = 1) +
  scale_fill_gradient(low = col_low, high = col_high, name = "Trips per\nhour slot") +
  scale_x_continuous(breaks = seq(0, 23, 3), expand = c(0, 0)) +
  labs(title = title, subtitle = subtitle, x = "Hour of day (start time)", y = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid = element_blank(), strip.text = element_text(face = "bold", hjust = 0),
        plot.title = element_text(face = "bold"), plot.background = element_rect(fill = "#fcfcfb", colour = NA))

ggsave("plots/who-rides-when.svg", p, width = 9, height = 5.6)
ggsave("plots/who-rides-when.png", p, width = 9, height = 5.6, dpi = 200)
