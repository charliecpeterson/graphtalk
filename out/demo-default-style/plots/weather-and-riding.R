# plots/weather-and-riding.R: run from out/<slug>/
library(ggplot2); library(readr)

# Edit here ---------------------------------------------------------------
title    <- "Riding rises to about 22 C, and rain takes 40 to 70 trips off a typical day"
subtitle <- "Mean trips per day by 4 C temperature band; rainy day = 1 mm or more (bands with under 3 days dropped)"
col_dry  <- "#2a78d6"; col_rain <- "#eb6834"
# -------------------------------------------------------------------------

d <- read_csv("data/weather-and-riding.csv", show_col_types = FALSE)
last <- do.call(rbind, lapply(split(d, d$rain), function(g) g[which.max(g$temp_band), ]))

p <- ggplot(d, aes(temp_band, mean_trips, colour = rain)) +
  geom_line(linewidth = 0.9) +
  geom_point(aes(size = days), shape = 21, fill = "#fcfcfb", stroke = 1.2) +
  geom_text(data = last, aes(label = rain), hjust = -0.15, size = 3.4, show.legend = FALSE) +
  scale_colour_manual(values = c("Dry day" = col_dry, "Rainy day" = col_rain), guide = "none") +
  scale_size_area(max_size = 5, name = "Days in band") +
  scale_x_continuous(breaks = seq(6, 30, 4), expand = expansion(mult = c(0.03, 0.2))) +
  labs(title = title, subtitle = subtitle, x = "Mean daily temperature (C, band midpoint)", y = "Trips per day") +
  theme_minimal(base_size = 11) +
  theme(panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"),
        plot.background = element_rect(fill = "#fcfcfb", colour = NA))

ggsave("plots/weather-and-riding.svg", p, width = 8, height = 4.6)
ggsave("plots/weather-and-riding.png", p, width = 8, height = 4.6, dpi = 200)
