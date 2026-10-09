# plots/calendar-of-the-year.R: run from out/bikeshare-five-questions/
library(ggplot2); library(readr)
paper <- "#f4efe4"; ink <- "#1f1d1a"; ink2 <- "#55504a"; rule <- "#cdc5b3"
theme_plate <- function() theme_minimal(base_size = 11, base_family = "serif") + theme(
  plot.background = element_rect(fill = paper, colour = NA), panel.background = element_rect(fill = paper, colour = NA),
  panel.grid = element_blank(), axis.line = element_line(colour = ink, linewidth = 0.3), axis.ticks = element_line(colour = ink2, linewidth = 0.3),
  plot.title = element_text(face = "bold", size = 17, colour = ink), plot.subtitle = element_text(face = "italic", size = 10, colour = ink2),
  plot.title.position = "plot", plot.margin = margin(14, 18, 10, 14), text = element_text(colour = ink))

# Edit here ---------------------------------------------------------------
title    <- "One day stands out: Saturday July 12, 712 trips."
subtitle <- "Trips per day, 2025. Darker is busier; outlined squares are the five busiest days."
col_low <- "#e6e6d8"; col_high <- "#0e3f43"; col_mid <- "#00929B"
# -------------------------------------------------------------------------

d <- read_csv("data/calendar-of-the-year.csv", show_col_types = FALSE)
d$wd <- factor(d$weekday, levels = 0:6, labels = c("Mon","Tue","Wed","Thu","Fri","Sat","Sun"))
d$wd <- factor(d$wd, levels = rev(levels(d$wd)))
d$half <- factor(ifelse(d$date < as.Date("2025-07-01"), "January to June", "July to December"), levels = c("January to June", "July to December"))
d$col <- ave(d$week, d$half, FUN = function(w) w - min(w))
top <- d[!is.na(d$top5_rank), ]

p <- ggplot(d, aes(col, wd, fill = trips)) +
  geom_tile(colour = paper, linewidth = 0.6) +
  geom_tile(data = top, fill = NA, colour = ink, linewidth = 0.7, width = 1, height = 1) +
  geom_text(data = top, aes(label = top5_rank), colour = "white", size = 3, family = "mono") +
  facet_wrap(~half, ncol = 1) + coord_equal() +
  scale_fill_gradientn(colours = c(col_low, "#b9d8d5", "#6fb8bb", col_mid, "#1C6D72", col_high), name = "trips") +
  labs(title = title, subtitle = subtitle, x = NULL, y = NULL) + theme_plate() +
  theme(axis.line = element_blank(), axis.text.x = element_blank(), axis.ticks = element_blank(),
        strip.text = element_text(face = "bold", hjust = 0, colour = ink2), legend.position = "bottom")

ggsave("plots/calendar-of-the-year.svg", p, width = 12, height = 6.75)
ggsave("plots/calendar-of-the-year.png", p, width = 12, height = 6.75, dpi = 200)
