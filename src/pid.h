// -*- mode: c; c-default-style: "k&r"; c-basic-offset: 4; indent-tabs-mode: nil; tab-width: 4 -*-
//
// Copyright (c) 2016 Benjamin J. Andre
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v.  2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.
//

// Single precision floating point implementation of a PID,
// proportional-integral-derivative, controller.

#ifndef PID_H_
#define PID_H_
#include <stdint.h>


// declare an opaque type for the public interface
typedef struct pid_data pid_data;

pid_data* pid_init(uint8_t const history_length, float const setpoint,
                   float const Kp, float const Ki, float const Kd);
void pid_free(pid_data** pid);

float pid_control(pid_data* pid, float const process_value, float const delta_time);

// access functions for unit testing and debugging logging.
uint8_t get_history_length(pid_data const *const pid);
float get_setpoint(pid_data const *const pid);
float get_Kp(pid_data const *const pid);
float get_Ki(pid_data const *const pid);
float get_Kd(pid_data const *const pid);

#endif // PID_H_
