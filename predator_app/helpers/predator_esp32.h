#pragma once

#include <furi.h>

typedef struct PredatorEsp32 PredatorEsp32;
typedef struct PredatorApp PredatorApp;

// ESP32 callback for received data
void predator_esp32_rx_callback(uint8_t* buf, size_t len, void* context);

// ESP32 management functions
PredatorEsp32* predator_esp32_alloc();
void predator_esp32_free(PredatorEsp32* esp32);
bool predator_esp32_send_command(PredatorApp* app, const char* command);
bool predator_esp32_is_connected(PredatorApp* app);

// WiFi attack functions
bool predator_esp32_wifi_scan(PredatorApp* app);
bool predator_esp32_wifi_deauth(PredatorApp* app, const char* target_mac);
bool predator_esp32_wifi_evil_twin(PredatorApp* app, const char* ssid);

// Bluetooth attack functions
bool predator_esp32_ble_scan(PredatorApp* app);
bool predator_esp32_ble_spam(PredatorApp* app);

// Status and control
bool predator_esp32_stop_attack(PredatorApp* app);
bool predator_esp32_get_status(PredatorApp* app);
