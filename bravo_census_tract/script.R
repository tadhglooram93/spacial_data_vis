library(tidycensus)
library(dplyr)
library(tigris)
library(sf)
library(ggplot2)
library(RColorBrewer)
library(gridExtra)
library(cowplot)
options(tigris_use_cache = TRUE)

load_variables(2010, "sf1") |> View()

# Define the variables you want to download
races <- c(
  total_pop = "P009001",
  hisp_pop = "P009002",
  white_pop ="P009005",
  black_pop = "P009006",
  asian_pop ="P009008" 
)

#Get population and geometry for suffolk county in MA
new_york_pop <- get_decennial(geography = "tract",
                            variables = races,
                            year = 2010,
                            state = "NY",
                            county = "New York",
                            output = "wide")

#Get ALAND from Tiger 
new_york_tracts <- tracts(state = "NY", county = "New York", year = 2010)
# keep relevant variables
new_york_tracts <- new_york_tracts[, c("GEOID10", "ALAND10", "geometry")]

#join suffolk_pop to suffolk_tracts
new_york_dat<- left_join(new_york_tracts, new_york_pop, by = c("GEOID10" = "GEOID"))

#convert ALAND10 to square miles:
new_york_dat <-new_york_dat %>%
  mutate(ALAND10_sqrmile = ALAND10*3.86102e-7)

# calculate population density
new_york_dat <- new_york_dat %>%
  mutate(pop_dense_sqmile = total_pop / ALAND10_sqrmile)

#calculate other_pop
new_york_dat <- new_york_dat %>%
  mutate(pop_other = total_pop - (hisp_pop + white_pop + black_pop + asian_pop))

#get the water area
ny_water <- area_water(state = "NY", county = "New York") |>st_union()

#Map one - chloropleth map illustrating the variation in tract-level population density across the county.
density_plot <- ggplot() +
  geom_sf(data = new_york_dat, aes(fill = pop_dense_sqmile),color="black") +
  scale_fill_gradientn(
    colors = brewer.pal(9, "YlOrRd"),
    space = "Lab",
    labels = scales::label_number(scale = 1e-3, suffix = "k"),
    na.value = "grey50",
    ) +  
  labs(title = "Population Density in New York County, NY",
       subtitle = "Population Density (people/sq.mi)",
       fill = "Legend",
       x = NULL,
       y = NULL) +
  geom_sf(data = ny_water,
          color = NA,
          fill = "lightblue") +
  geom_sf(color = "gray25",
          fill = NA) +
  theme(legend.position = c(0.1, 0.89)) +
  theme_void()

#Map two - density map illustrating the distribution of racial/ethnic groups across the county
pts_hisp <- st_sample(new_york_dat,
                       size = round(new_york_dat$hisp_pop/200))
pts_white <- st_sample(new_york_dat,
                          size = round(new_york_dat$white_pop/200))
pts_black <- st_sample(new_york_dat,
                          size = round(new_york_dat$black_pop/200))  
pts_asian <- st_sample(new_york_dat,
                          size = round(new_york_dat$asian_pop/200)) 
pts_other <- st_sample(new_york_dat,
                       size = round(new_york_dat$pop_other/200)) 

# Map 2 - dot density
dot_density_plot <- ggplot() +
  geom_sf(data = new_york_dat, fill = "white",color = "black") +
  geom_sf(data = pts_hisp,
          aes(color = "Hispanic"),
          size = 0.1) +
  geom_sf(data = pts_white,
          aes(color = "White"),
          size = 0.1) +
  geom_sf(data = pts_black,
          aes(color = "Black"),
          size = 0.1) +
  geom_sf(data = pts_asian,
          aes(color = "Asian"),
          size = 0.1) +
  geom_sf(data = pts_other,
          aes(color = "Other"),
          size = 0.1) +
  labs(title = "Dot Density of Race in New York County, NY",
       subtitle = "1 dot = 200 people",
       x = NULL,
       y = NULL) +
  scale_color_manual(
    values = c(Hispanic = "#ffff99", White = "#7fc97f", Black = "#beaed4", Asian = "#fdc086", Other = "grey"),
  ) +
  guides(
    color = guide_legend(
      title = "Legend",
      override.aes = list(size = 5)  # Adjust size for larger dots in the legend
    )
  ) +
  theme(legend.position = c(0.1, 0.89)) +
  geom_sf(data = ny_water, color = NA, fill = "lightblue") +
  theme_void()

# arrange maps side by side 
combined_plots <- grid.arrange(density_plot, dot_density_plot, ncol = 2)

# Set the dashboard title
plot_title <- ggdraw() +
  draw_text("Assigment Bravo - Population and Racial/Ethnic Distribution in New York
            ", x = 0.4, y = 0.1, size = 20, hjust = 0.5,fontface = "bold")
final_plot <- plot_grid(plot_title, combined_plots, ncol = 1, rel_heights = c(0.1, 1))
# Set the background color of the entire plot to light grey
final_plot <- final_plot +
  theme(panel.background = element_rect(fill = "#f8f9f5"))
final_plot