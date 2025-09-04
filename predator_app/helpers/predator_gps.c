#include "../predator_i.h"
#include <furi_hal_gpio.h>
#include <furi_hal_serial.h>
#include <furi_hal_bus.h>
#include <string.h>
#include <stdlib.h>

#define GPS_UART_BAUD PREDATOR_GPS_UART_BAUD
#define GPS_BUFFER_SIZE 512

static void predator_gps_rx_callback(uint8_t* data, size_t size, void* context) {
    PredatorApp* app = context;
    
    // Parse incoming GPS data
    for(size_t i = 0; i < size; i++) {
        if(data[i] == '\n') {
            // Process complete NMEA sentence
            static char nmea_buffer[128];
            static size_t nmea_pos = 0;
            
            if(nmea_pos > 0) {
                nmea_buffer[nmea_pos] = '\0';
                predator_gps_parse_nmea(app, nmea_buffer);
                nmea_pos = 0;
            }
        } else if(data[i] != '\r' && nmea_pos < sizeof(nmea_buffer) - 1) {
            static char nmea_buffer[128];
            static size_t nmea_pos = 0;
            nmea_buffer[nmea_pos++] = data[i];
        }
    }
}

void predator_gps_init(PredatorApp* app) {
    // Check GPS power switch state (front left switch must be down)
    furi_hal_gpio_init(PREDATOR_GPS_POWER_SWITCH, GpioModeInput, GpioPullUp, GpioSpeedLow);
    if(furi_hal_gpio_read(PREDATOR_GPS_POWER_SWITCH)) {
        app->gps_connected = false;
        return; // GPS switch is up (using internal battery)
    }
    
    // Initialize UART for GPS communication on pins 13,14
    furi_hal_gpio_init(PREDATOR_GPS_UART_TX_PIN, GpioModeAltFunctionPushPull, GpioPullNo, GpioSpeedVeryHigh);
    furi_hal_gpio_init(PREDATOR_GPS_UART_RX_PIN, GpioModeAltFunctionPushPull, GpioPullNo, GpioSpeedVeryHigh);
    furi_hal_serial_init(FuriHalSerialIdLpuart, GPS_UART_BAUD);
    furi_hal_serial_enable_direction(FuriHalSerialIdLpuart, FuriHalSerialDirectionRx);
    furi_hal_serial_enable_direction(FuriHalSerialIdLpuart, FuriHalSerialDirectionTx);
    
    app->gps_connected = false;
    app->latitude = 0.0f;
    app->longitude = 0.0f;
    app->satellites = 0;
}

void predator_gps_deinit(PredatorApp* app) {
    furi_hal_serial_deinit(FuriHalSerialIdLpuart);
    app->gps_connected = false;
}

void predator_gps_update(PredatorApp* app) {
    // GPS data is updated via UART callback
    UNUSED(app);
}

bool predator_gps_parse_nmea(PredatorApp* app, const char* sentence) {
    if(!app || !sentence) return false;
    
    // Parse NMEA sentences (GPGGA, GPRMC, etc.)
    if(strncmp(sentence, "$GPGGA", 6) == 0 || strncmp(sentence, "$GNGGA", 6) == 0) {
        // Parse GGA sentence for coordinates and satellite count
        char* sentence_copy = strdup(sentence);
        char* token = strtok(sentence_copy, ",");
        int field = 0;
        
        while(token != NULL && field < 15) {
            switch(field) {
                case 2: // Latitude
                    if(strlen(token) > 0) {
                        float lat_raw = atof(token);
                        // Convert DDMM.MMMM to DD.DDDD
                        int degrees = (int)(lat_raw / 100);
                        float minutes = lat_raw - (degrees * 100);
                        app->latitude = degrees + (minutes / 60.0f);
                    }
                    break;
                case 4: // Longitude
                    if(strlen(token) > 0) {
                        float lon_raw = atof(token);
                        // Convert DDDMM.MMMM to DDD.DDDD
                        int degrees = (int)(lon_raw / 100);
                        float minutes = lon_raw - (degrees * 100);
                        app->longitude = degrees + (minutes / 60.0f);
                    }
                    break;
                case 7: // Number of satellites
                    if(strlen(token) > 0) {
                        app->satellites = atoi(token);
                    }
                    break;
            }
            token = strtok(NULL, ",");
            field++;
        }
        
        if(app->satellites > 0) {
            app->gps_connected = true;
        }
        
        free(sentence_copy);
        return true;
    }
    
    return false;
}

bool predator_gps_get_coordinates(PredatorApp* app, float* lat, float* lon) {
    if(!app || !lat || !lon) return false;
    
    *lat = app->latitude;
    *lon = app->longitude;
    
    return app->gps_connected && app->satellites > 0;
}

uint32_t predator_gps_get_satellites(PredatorApp* app) {
    if(!app) return 0;
    return app->satellites;
}

bool predator_gps_is_connected(PredatorApp* app) {
    if(!app) return false;
    return app->gps_connected;
}
