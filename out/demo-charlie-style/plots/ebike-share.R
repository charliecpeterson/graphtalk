# plots/ebike-share.R: run from out/bikeshare-five-questions/
library(ggplot2); library(readr)
paper <- "#f4efe4"; ink <- "#1f1d1a"; ink2 <- "#55504a"; rule <- "#cdc5b3"
theme_plate <- function() theme_minimal(base_size = 11, base_family = "serif") + theme(
  plot.background = element_rect(fill = paper, colour = NA), panel.background = element_rect(fill = paper, colour = NA),
  panel.grid = element_blank(), axis.line = element_line(colour = ink, linewidth = 0.3), axis.ticks = element_line(colour = ink2, linewidth = 0.3),
  plot.title = element_text(face = "bold", size = 17, colour = ink), plot.subtitle = element_text(face = "italic", size = 10, colour = ink2),
  plot.title.position = "plot", plot.margin = margin(14, 18, 10, 14), text = element_text(colour = ink))

# Edit here ---------------------------------------------------------------
title    <- "Every neighborhood gained e-bikes, yet the city share fell."
subtitle <- "Share of trips on e-bikes: January to June (open circle) to July to December (arrow tip). Harbor Flats opened July 1, so it has no first half."
col_main <- "#00929B"; col_city <- "#D8435A"
# -------------------------------------------------------------------------

d <- read_csv("data/ebike-share.csv", show_col_types = FALSE)
d$series <- ifelse(d$neighborhood == "All trips", "city", "hood")
d$y <- factor(d$neighborhood, levels = rev(d$neighborhood))

p <- ggplot(d, aes(y = y, colour = series)) +
  geom_segment(aes(x = h1, xend = h2, yend = y), arrow = arrow(length = unit(2.2, "mm"), type = "closed"), linewidth = 0.8) +
  geom_point(aes(x = h1), shape = 21, fill = paper, size = 2.6, stroke = 0.9) +
  geom_text(aes(x = ifelse(h2 < h1, h2, h2), label = sprintf("%.1f%%", h2)), hjust = ifelse(d$h2 < d$h1, 1.4, -0.4), size = 3.2, colour = ink2, family = "mono") +
  geom_hline(yintercept = 1.5, colour = ink2, linewidth = 0.25) +
  scale_colour_manual(values = c(hood = col_main, city = col_city), guide = "none") +
  scale_x_continuous(limits = c(10, 70)) +
  labs(title = title, subtitle = subtitle, x = "% of trips on e-bikes", y = NULL) + theme_plate() +
  theme(panel.grid.major.y = element_line(colour = rule, linewidth = 0.25), axis.line.y = element_blank(), axis.ticks.y = element_blank())

ggsave("plots/ebike-share.svg", p, width = 12, height = 6.75)
ggsave("plots/ebike-share.png", p, width = 12, height = 6.75, dpi = 200)
