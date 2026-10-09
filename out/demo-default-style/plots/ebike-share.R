# plots/ebike-share.R: run from out/<slug>/
library(ggplot2); library(readr)

# Edit here ---------------------------------------------------------------
title    <- "Every neighborhood gained e-bike share, yet the city total slipped"
subtitle <- "Share of trips on e-bikes by start neighborhood, Jan to Jun (open dot) vs Jul to Dec (arrow tip). Harbor Flats only has second-half trips."
col_main <- "#2a78d6"; col_city <- "#eb6834"
# -------------------------------------------------------------------------

d <- read_csv("data/ebike-share.csv", show_col_types = FALSE)
d$series <- ifelse(d$neighborhood == "All trips", "city", "hood")
d$y <- reorder(d$neighborhood, ifelse(d$neighborhood == "All trips", -1, d$h2))
d$lab <- ifelse(is.na(d$h1), sprintf("%.1f%% (opened in H2)", d$h2), sprintf("%.1f%%", d$h2))

p <- ggplot(d, aes(y = y, colour = series)) +
  geom_segment(aes(x = h1, xend = h2, yend = y), arrow = arrow(length = unit(2, "mm")), linewidth = 0.8, na.rm = TRUE) +
  geom_point(aes(x = h1), shape = 21, fill = "#fcfcfb", size = 2.8, stroke = 1.1, na.rm = TRUE) +
  geom_point(data = d[is.na(d$h1), ], aes(x = h2), size = 2.8) +
  geom_text(aes(x = pmax(h1, h2, na.rm = TRUE), label = lab), hjust = -0.15, size = 3.2, colour = "#0b0b0b") +
  scale_colour_manual(values = c(hood = col_main, city = col_city), guide = "none") +
  scale_x_continuous(expand = expansion(mult = c(0.02, 0.22))) +
  labs(title = title, subtitle = subtitle, x = "% of trips on e-bikes", y = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.major.y = element_blank(), panel.grid.minor = element_blank(), plot.title = element_text(face = "bold"),
        plot.subtitle = element_text(size = 8.5), plot.background = element_rect(fill = "#fcfcfb", colour = NA))

ggsave("plots/ebike-share.svg", p, width = 8, height = 4.4)
ggsave("plots/ebike-share.png", p, width = 8, height = 4.4, dpi = 200)
