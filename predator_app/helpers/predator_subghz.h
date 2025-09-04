#pragma once

#include "../predator_i.h"

void predator_subghz_init(PredatorApp* app);
void predator_subghz_deinit(PredatorApp* app);
void predator_subghz_start_car_bruteforce(PredatorApp* app, uint32_t frequency);
void predator_subghz_send_car_key(PredatorApp* app, uint32_t key_code);
void predator_subghz_start_jamming(PredatorApp* app, uint32_t frequency);
void predator_subghz_send_tesla_charge_port(PredatorApp* app);
