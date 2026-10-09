# plots/who-rides-when.R: run from out/bikeshare-five-questions/
library(ggplot2); library(readr)
paper <- "#f4efe4"; ink <- "#1f1d1a"; ink2 <- "#55504a"; rule <- "#cdc5b3"
theme_plate <- function() theme_minimal(base_size = 11, base_family = "serif") + theme(
  plot.background = element_rect(fill = paper, colour = NA), panel.background = element_rect(fill = paper, colour = NA),
  panel.grid = element_blank(), axis.line = element_line(colour = ink, linewidth = 0.3), axis.ticks = element_line(colour = ink2, linewidth = 0.3),
  plot.title = element_text(face = "bold", size = 17, colour = ink), plot.subtitle = element_text(face = "italic", size = 10, colour = ink2),
  plot.title.position = "plot", plot.margin = margin(14, 18, 10, 14), text = element_text(colour = ink))

# Edit here ---------------------------------------------------------------
title    <- "Members ride at commute hours, casual riders on weekends."
subtitle <- "Average trips per hour by weekday and hour, 2025. Circle area is proportional to trips, one scale for both panels."
col_member <- "#00929B"; col_casual <- "#B87800"; max_size <- 4.2
# -------------------------------------------------------------------------

d <- read_csv("data/who-rides-when.csv", show_col_types = FALSE)
d$weekday <- factor(d$weekday, levels = rev(c("Mon","Tue","Wed","Thu","Fri","Sat","Sun")))
d$rider_type <- factor(d$rider_type, levels = c("member","casual"), labels = c("Members","Casual riders"))

p <- ggplot(d, aes(hour, weekday, size = avg_trips, colour = rider_type)) +
  geom_hline(aes(yintercept = as.numeric(weekday)), colour = rule, linewidth = 0.25) +
  geom_point() + facet_wrap(~rider_type) +
  scale_size_area(max_size = max_size, guide = "none") +
  scale_colour_manual(values = c(Members = col_member, "Casual riders" = col_casual), guide = "none") +
  scale_x_continuous(breaks = seq(0, 21, 3), labels = function(x) paste0(x, ":00")) +
  labs(title = title, subtitle = subtitle, x = NULL, y = NULL) +
  theme_plate() + theme(axis.line = element_blank(), strip.text = element_text(face = "bold", hjust = 0, size = 11, colour = ink2))

ggsave("plots/who-rides-when.svg", p, width = 12, height = 6.75)
ggsave("plots/who-rides-when.png", p, width = 12, height = 6.75, dpi = 200)
