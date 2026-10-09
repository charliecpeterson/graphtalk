# plots/station-net-flow.R: run from out/<slug>/
library(ggplot2); library(readr)

# Edit here ---------------------------------------------------------------
title    <- "Downtown and Harbor Flats fill up; University, Hillcrest and Greenway drain"
subtitle <- "Net flow per station, 2025 (trips ending minus trips starting). Blue stations fill, red stations drain; the biggest four each way are named."
col_fill <- "#2a78d6"; col_drain <- "#e34948"; col_mid <- "#f0efec"
# -------------------------------------------------------------------------

d <- read_csv("data/station-net-flow.csv", show_col_types = FALSE)
d$r <- rank(-d$net, ties.method = "first")
lab <- d[d$r <= 4 | d$r > nrow(d) - 4, ]
lab$short <- sprintf("%s (%+d)", lab$station_name, lab$net)
# label placement: side (hjust) and vertical nudge so neighbouring labels do not collide
lab$dy <- 0; lab$dy[lab$r == 1] <- 0.0045; lab$dy[lab$r == 4] <- -0.0045; lab$dy[lab$r == nrow(d)] <- -0.0035
lab$hj <- ifelse(lab$net > 0, 0, 1); lab$dx <- ifelse(lab$hj == 0, 0.0022, -0.0022)
lim <- max(abs(d$net))

p <- ggplot(d, aes(lon, lat)) +
  geom_point(aes(size = abs(net), fill = net), shape = 21, colour = "#fcfcfb", stroke = 0.6) +
  geom_text(data = lab, aes(lon + dx, lat + dy, label = short, hjust = hj), size = 2.8) +
  scale_fill_gradient2(low = col_drain, mid = col_mid, high = col_fill, midpoint = 0, limits = c(-lim, lim), name = "Net trips") +
  scale_size_area(max_size = 9, guide = "none") +
  scale_x_continuous(expand = expansion(mult = 0.25)) +
  coord_fixed(ratio = 1 / cos(37.75 * pi / 180)) +
  labs(title = title, subtitle = subtitle, x = NULL, y = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid = element_blank(), axis.text = element_blank(), plot.title = element_text(face = "bold"),
        plot.subtitle = element_text(size = 8.5), plot.background = element_rect(fill = "#fcfcfb", colour = NA))

ggsave("plots/station-net-flow.svg", p, width = 9, height = 6)
ggsave("plots/station-net-flow.png", p, width = 9, height = 6, dpi = 200)
