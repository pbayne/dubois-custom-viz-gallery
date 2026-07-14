# Authoritative Vega-Lite example slugs (from vega-lite site/_data/examples.json)

Goal: the gallery should represent every **feasible** slug. When filling gaps, add a
chart per missing feasible slug (id prefix `g3_<slug>` is fine). Skip the INFEASIBLE
ones listed at the bottom (they can't render in a static custom-viz widget).

## Single-View Plots
- **Bar Charts (24):** bar, bar_size_responsive, bar_aggregate, bar_aggregate_sort_by_encoding, bar_grouped, bar_grouped_repeated*, stacked_bar_weather, stacked_bar_count_corner_radius_mark, stacked_bar_h, stacked_bar_normalize, stacked_bar_h_normalized_labeled, bar_gantt, bar_color_disabled_scale, bar_layered_transparent, bar_diverging_stack_population_pyramid, bar_diverging_stack_transform, layer_bar_labels, **layer_bar_labels_grey**, bar_month_temporal_initial, bar_month_temporal_band_center, bar_negative, bar_negative_horizontal_label, bar_axis_space_saving, bar_heatlane
- **Histograms, Density, Dot (15):** histogram, bar_binned_data, histogram_log, histogram_nonlinear, histogram_rel_freq, area_density, area_density_stacked, circle_binned, rect_binned_heatmap, area_cumulative_freq, layer_cumulative_histogram, circle_wilkinson_dotplot, isotype_bar_chart, isotype_bar_chart_emoji(SKIP), bar_percent_of_total
- **Scatter & Strip (14):** point_2d, tick_dot, tick_strip, point_color_with_shape, circle_binned, point_bubble, point_invalid_color, circle, circle_bubble_health_income, circle_natural_disasters, text_scatterplot_colored, scatter_image(SKIP), circle_custom_tick_labels, point_offset_random
- **Line Charts (20):** line, line_overlay, line_overlay_stroked, line_color, repeat_layer*, line_color_halo, line_slope, line_step, line_monotone, line_conditional_axis, connected_scatterplot, line_bump, trail_color, trail_comet, line_skip_invalid_mid_overlay, layer_line_co2_concentration, window_rank, sequence_line_fold, line_strokedash, line_dashed_part
- **Area & Streamgraphs (7):** area, area_gradient, area_overlay, stacked_area, stacked_area_normalize, stacked_area_stream, area_horizon
- **Table-based (8):** rect_heatmap, rect_heatmap_weather, rect_binned_heatmap, circle_github_punchcard, layer_text_heatmap, rect_lasagna, rect_mosaic_labelled_with_offset, point_angle_windvector(SKIP-no wind dir)
- **Circular (6):** arc_pie, arc_pie_normalize_tooltip, arc_donut, layer_arc_label, arc_radial, arc_pie_pyramid
- **Advanced Calculations (21):** bar_percent_of_total, joinaggregate_mean_difference, joinaggregate_mean_difference_by_year, joinaggregate_residual_graph, window_rank, waterfall_chart, window_top_k, window_top_k_others, lookup, area_cumulative_freq, layer_cumulative_histogram, parallel_coordinate, bar_argmax, layer_line_mean_point_raw, layer_line_rolling_mean_point_raw, layer_line_window, point_quantile_quantile, layer_point_line_regression, layer_point_line_loess, window_impute_null, ternary

## Composite Marks
- **Error Bars & Bands (4):** layer_point_errorbar_ci, layer_point_errorbar_stdev, layer_line_errorband_ci, layer_scatter_errorband_1D_stdev_global_mean
- **Box Plots (3):** boxplot_minmax_2D_vertical, boxplot_2D_vertical, boxplot_preaggregated

## Layered Plots
- **Labeling & Annotation (12):** layer_bar_labels, layer_bar_fruit, layer_text_heatmap, layer_line_co2_concentration, layer_bar_annotations, layer_precipitation_mean, layer_histogram_global_mean, layer_falkensee, layer_line_mean_point_raw, layer_line_rolling_mean_point_raw, layer_likert, concat_layer_voyager_result(SKIP-concat)
- **Other Layered (7):** layer_candlestick, layer_ranged_dot, facet_bullet(bullet-ok/no facet), layer_dual_axis(SKIP-dual axis), area_horizon, bar_layered_weather, wheat_wages

## Maps (feasible subset)
- geo_choropleth (native choropleth-map ✓ have CA/LA), geo_circle (point ✓), geo_text (place city/airport labels), geo_rule/geo_line (SKIP-need route pairs), geo_layer_line_london (SKIP-no data), geo_* facet/repeat/interactive (SKIP)

## INFEASIBLE — do NOT implement (static custom-viz can't do these)
- All **Interactive** (32): interactive_*, selection_*, point_href, brush_table, isotype_grid, param_search_input, dynamic_color_legend, bar_count_minimap, interactive_index_chart, interactive_bin_extent, airport_connections, interactive_global_development
- All **Faceting/Trellis** (10): trellis_*, area_density_facet, facet_grid_bar
- All **Repeat & Concat** (8): repeat_layer, vconcat_weather, repeat_histogram, interactive_splom, concat_*, nested_concat_align
- One-offs: scatter_image, point_angle_windvector, ternary(niche—optional), layer_dual_axis, geo_layer_line_london
(*bar_grouped_repeated / repeat_layer use the repeat operator → implement the NON-repeat equivalent instead, which we already have.)
