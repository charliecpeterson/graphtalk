# plots/station-net-flow.R: run from out/bikeshare-five-questions/
library(ggplot2); library(readr)
paper <- "#f4efe4"; ink <- "#1f1d1a"; ink2 <- "#55504a"; rule <- "#cdc5b3"
theme_plate <- function() theme_minimal(base_size = 11, base_family = "serif") + theme(
  plot.background = element_rect(fill = paper, colour = NA), panel.background = element_rect(fill = paper, colour = NA),
  panel.grid = element_blank(), axis.line = element_line(colour = ink, linewidth = 0.3), axis.ticks = element_line(colour = ink2, linewidth = 0.3),
  plot.title = element_text(face = "bold", size = 17, colour = ink), plot.subtitle = element_text(face = "italic", size = 10, colour = ink2),
  plot.title.position = "plot", plot.margin = margin(14, 18, 10, 14), text = element_text(colour = ink))

# Edit here ---------------------------------------------------------------
title    <- "Higher stations lose bikes and lower ones gain them, by up to 1,400 a year."
subtitle <- "Net flow per station, 2025: arrivals minus departures. The seven biggest drains and fills."
col_drain <- "#00929B"; col_fill <- "#D8435A"; n_each <- 7
# -------------------------------------------------------------------------

d <- read_csv("data/station-net-flow.csv", show_col_types = FALSE)
d <- d[order(d$net), ]
ext <- rbind(head(d, n_each), tail(d, n_each))
ext$y <- factor(ext$station_name, levels = ext$station_name)
ext$dir <- ifelse(ext$net > 0, "fill", "drain")

p <- ggplot(ext, aes(y = y, colour = dir)) +
  geom_vline(xintercept = 0, colour = ink, linewidth = 0.4) +
  geom_segment(aes(x = 0, xend = net, yend = y), linewidth = 0.9) + geom_point(aes(x = net), size = 2.6) +
  geom_text(aes(x = net, label = sprintf("%+d", net)), hjust = ifelse(ext$net > 0, -0.3, 1.3), size = 3, colour = ink2, family = "mono") +
  geom_text(aes(x = 0, label = station_name), hjust = ifelse(ext$net > 0, 1.05, -0.05), size = 3.2, colour = ink) +
  scale_colour_manual(values = c(drain = col_drain, fill = col_fill), guide = "none") +
  scale_x_continuous(limits = c(-2000, 2000)) + scale_y_discrete(labels = NULL) +
  labs(title = title, subtitle = subtitle, x = "net bikes in a year (arrivals minus departures)", y = NULL) + theme_plate() +
  theme(axis.line.y = element_blank(), axis.ticks.y = element_blank())

ggsave("plots/station-net-flow.svg", p, width = 12, height = 6.75)
ggsave("plots/station-net-flow.png", p, width = 12, height = 6.75, dpi = 200)
