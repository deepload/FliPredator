#pragma once

#include <furi.h>

typedef struct PredatorGps PredatorGps;
typedef struct PredatorApp PredatorApp;

// GPS callback for received data
void predator_gps_rx_callback(uint8_t* buf, size_t len, void* context);

// GPS management functions
PredatorGps* predator_gps_alloc();
void predator_gps_free(PredatorGps* gps);
bool predator_gps_get_coordinates(PredatorApp* app, float* lat, float* lon);
uint32_t predator_gps_get_satellites(PredatorApp* app);
bool predator_gps_is_connected(PredatorApp* app);

// GPS data parsing
bool predator_gps_parse_nmea(PredatorApp* app, const char* nmea_sentence);
