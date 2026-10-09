# plots/weather-and-riding.R: run from out/bikeshare-five-questions/
library(ggplot2); library(readr)
paper <- "#f4efe4"; ink <- "#1f1d1a"; ink2 <- "#55504a"; rule <- "#cdc5b3"
theme_plate <- function() theme_minimal(base_size = 11, base_family = "serif") + theme(
  plot.background = element_rect(fill = paper, colour = NA), panel.background = element_rect(fill = paper, colour = NA),
  panel.grid = element_blank(), axis.line = element_line(colour = ink, linewidth = 0.3), axis.ticks = element_line(colour = ink2, linewidth = 0.3),
  plot.title = element_text(face = "bold", size = 17, colour = ink), plot.subtitle = element_text(face = "italic", size = 10, colour = ink2),
  plot.title.position = "plot", plot.margin = margin(14, 18, 10, 14), text = element_text(colour = ink))

# Edit here ---------------------------------------------------------------
title    <- "Warmth adds trips; a rainy day takes back 4 to 16% of them."
subtitle <- "Mean trips per day by daily mean temperature, on dry days (under 2 mm) and rainy days (2 mm or more)."
col_dry <- "#00929B"; col_rain <- "#D8435A"
# -------------------------------------------------------------------------

d <- read_csv("data/weather-and-riding.csv", show_col_types = FALSE)
d$temp_bin_c <- factor(d$temp_bin_c, levels = c("<7","7-10","10-13","13-16","16-19","19-22",">22"))
last <- do.call(rbind, lapply(split(d, d$rain), function(g) g[which.max(as.integer(g$temp_bin_c)), ]))
last$label <- ifelse(last$rain == "dry", "Dry days", "Rainy days")

p <- ggplot(d, aes(temp_bin_c, mean_trips, colour = rain, group = rain)) +
  geom_line(linewidth = 1.1) + geom_point(size = 2.3) +
  geom_text(data = last, aes(label = label), hjust = -0.2, fontface = "italic", colour = ink, size = 3.8) +
  scale_colour_manual(values = c(dry = col_dry, rain = col_rain), guide = "none") +
  scale_y_continuous(limits = c(0, 520)) + scale_x_discrete(expand = expansion(add = c(0.3, 1.1))) +
  labs(title = title, subtitle = subtitle, x = "daily mean temperature, degrees C", y = "trips per day") + theme_plate()

ggsave("plots/weather-and-riding.svg", p, width = 12, height = 6.75)
ggsave("plots/weather-and-riding.png", p, width = 12, height = 6.75, dpi = 200)
