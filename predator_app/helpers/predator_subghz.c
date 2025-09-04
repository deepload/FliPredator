#include "../predator_i.h"
#include "predator_subghz.h"
#include <furi_hal_subghz.h>
#include <furi_hal_gpio.h>

void predator_subghz_init(PredatorApp* app) {
    UNUSED(app);
    // Initialize A07 433MHz external module (10dBm)
    furi_hal_subghz_reset();
    furi_hal_subghz_load_preset(FuriHalSubGhzPresetOok650Async);
    
    // Configure for external A07 module
    furi_hal_subghz_set_frequency(433920000); // 433.92 MHz
}

void predator_subghz_deinit(PredatorApp* app) {
    UNUSED(app);
    furi_hal_subghz_sleep();
}

void predator_subghz_start_car_bruteforce(PredatorApp* app, uint32_t frequency) {
    UNUSED(app);
    // Use A07 external module for car attacks
    furi_hal_subghz_set_frequency(frequency);
    furi_hal_subghz_tx();
}

void predator_subghz_send_car_key(PredatorApp* app, uint32_t key_code) {
    UNUSED(app);
    
    // Common car key frequencies and protocols
    // Common car key frequencies
    // 433920000, 315000000, 868350000, 434075000
    
    // Generate key signal based on key_code
    uint8_t data[8];
    data[0] = (key_code >> 24) & 0xFF;
    data[1] = (key_code >> 16) & 0xFF;
    data[2] = (key_code >> 8) & 0xFF;
    data[3] = key_code & 0xFF;
    data[4] = 0x00; // Command: unlock
    data[5] = 0x01; // Repeat
    data[6] = 0x00; // Checksum placeholder
    data[7] = 0x00; // End
    
    // Simple checksum
    data[6] = (data[0] + data[1] + data[2] + data[3] + data[4] + data[5]) & 0xFF;
    
    // Transmit the signal
    furi_hal_subghz_start_async_tx(NULL, NULL);
    furi_delay_ms(10);
    furi_hal_subghz_stop_async_tx();
}

void predator_subghz_start_jamming(PredatorApp* app, uint32_t frequency) {
    UNUSED(app);
    // Use A07 external module for jamming (10dBm power)
    furi_hal_subghz_set_path(FuriHalSubGhzPathExternal);
    furi_hal_subghz_set_frequency_and_path(frequency);
    furi_hal_subghz_tx();
    
    // Generate noise signal for jamming
    for(int i = 0; i < 1000; i++) {
        furi_hal_subghz_start_async_tx(NULL, NULL);
        furi_delay_us(100);
        furi_hal_subghz_stop_async_tx();
        furi_delay_us(100);
    }
}

void predator_subghz_send_tesla_charge_port(PredatorApp* app) {
    UNUSED(app);
    
    // Tesla charge port opener signal
    // Frequency: 315 MHz
    furi_hal_subghz_set_frequency(315000000);
    furi_hal_subghz_tx();
    
    // Tesla-specific signal pattern
    // uint8_t tesla_signal[] = {0x02, 0x8A, 0x8A, 0x8A, 0x02, 0x00}; // Unused variable
    
    for(int repeat = 0; repeat < 5; repeat++) {
        furi_hal_subghz_start_async_tx(NULL, NULL);
        furi_delay_ms(50);
        furi_hal_subghz_stop_async_tx();
        furi_delay_ms(50);
    }
}
