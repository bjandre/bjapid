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
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include "pid.h"

struct pid_data {
    float setpoint;
    float Kp;
    float Ki;
    float Kd;
    float integral;
    uint8_t current;
    uint8_t history_length;
    float *interval;
    float *history;
};

struct pid_data* pid_init(uint8_t const history_length, float const setpoint, 
                          float const Kp, float const Ki, float const Kd) {
    // by definition gains must be non-negative
    assert(Kp >= 0.0f);
    assert(Ki >= 0.0f);
    assert(Kp >= 0.0f);
    
    struct pid_data* pid;
    pid = malloc(sizeof(struct pid_data));
    pid->setpoint = setpoint;
    pid->Kp = Kp;
    pid->Ki = Ki;
    pid->Kd = Kd;
    pid->integral = 0.0f;
    pid->current = 0;
    pid->history_length = history_length;
    pid->interval = malloc(pid->history_length * sizeof(float));
    pid->history = malloc(pid->history_length * sizeof(float));

    // initialize the history and calculate the initial integral
    // assuming perfect control. This should result in 
    for (uint8_t i = 0; i < pid->history_length; i++) {
        pid->history[i] = pid->setpoint;
        pid->interval[i] = 1.0;
        pid->integral += (pid->setpoint - pid->history[i]) * pid->interval[i];
    }
    return pid;
}

void pid_free(struct pid_data** pid) {
    free((*pid)->history);
    free((*pid)->interval);
    free(*pid);
    *pid = NULL;
}

float pid_control(pid_data *pid, float const process_value, float const delta_time) {
    // calculate the PID output as:
    //
    //   e(t) = PS - PV(t)
    //
    //   dP(t) = PV(t) - PV(t-1)
    //
    //   C(t) = Kp * e(t) + Ki * Integral[t-H, t, e(t)*dt] + Kd * dPV(t)/dt
    //
    //   Kp >= 0, Ki >= 0, Kd >= 0
    //
    // where:
    //   t = time index
    //   C(t) = PID control output at time t
    //   Kp, Ki, Kd = proportional, integral and derivative gains
    //   e(t) = process error at time t
    //   PS = set point
    //   PV(t) = process value at time t
    //   H = history length
    //   dt = delta time between process samples
    //
    // Note: Calculating error as setpoint - process value, but the
    // derivative is based on the process variable instead of the
    // error.
    
    float error = pid->setpoint - process_value;
    
    uint8_t tm1 = pid->current; // time index t-1, where current time is t

    // update the stored integral by subtracting out the oldest stored
    // value and adding in the current value
    float hist_error = pid->setpoint - pid->history[tm1];
    float hist_integral = hist_error * pid->interval[tm1];
    pid->integral -= hist_integral;
    pid->integral += error * delta_time;
    
    float derivative = (process_value - pid->history[tm1]) / delta_time;
    
    float output = pid->Kp * error + pid->Ki * pid->integral + pid->Kd * derivative;

    // update the circular history buffers with the current values
    // then increment the current location.
    pid->history[tm1] = process_value;
    pid->interval[tm1] = delta_time;
    tm1++;
    tm1 %= pid->history_length;
    pid->current = tm1;
        
    if (false) {
        printf("error = %f\n", error);
        printf("hist_error = %f\n", hist_error);
        printf("hist_integral = %f\n", hist_integral);
        printf("integral = %f\n", pid->integral);
        printf("derivative = %f\n", derivative);
        printf("output = %f\n", output);
    }
    return output;
}

// access functions for unit testing and debugging logging
uint8_t get_history_length(pid_data const *const pid) {
    return pid->history_length;
}

float get_setpoint(pid_data const *const pid) {
    return pid->setpoint;
}

float get_Kp(pid_data const *const pid) {
    return pid->Kp;
}

float get_Ki(pid_data const *const pid) {
    return pid->Ki;
}

float get_Kd(pid_data const *const pid) {
    return pid->Kd;
}
