// -*- mode: c; c-default-style: "k&r"; c-basic-offset: 4; indent-tabs-mode: nil; tab-width: 4 -*-

//
// Copyright (c) 2015 Benjamin J. Andre
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v.  2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.
// 

#include <inttypes.h>
#include <limits.h>

#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>

#include <stdio.h>
#include <math.h>

#include <cmocka.h>

#include "pid.h"

float const epsilon = 1.0e-8f;

static void test_pid_init(void **state) {
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 1.0;
    float Ki = 1.0;
    float Kd = 1.0;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);
    assert_non_null(pid);
}

static void test_pid_free(void **state) {
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 1.0;
    float Ki = 1.0;
    float Kd = 1.0;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);
    pid_free(&pid);
    assert_null(pid);
}

static void test_pid_init_values(void **state) {
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 1.0f;
    float Ki = 2.0f;
    float Kd = 3.0f;

    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);
    
    uint8_t received_hist = get_history_length(pid);
    assert_int_equal(hist_size, received_hist);
    
    float received = 0.0f;
    received = get_setpoint(pid);
    assert_true(fabs(setpoint - received) < epsilon);
    
    received = get_Kp(pid);
    assert_true(fabs(Kp - received) < epsilon);
    
    received = get_Ki(pid);
    assert_true(fabs(Ki - received) < epsilon);
    
    received = get_Kd(pid);
    assert_true(fabs(Kd - received) < epsilon);
    
    pid_free(&pid);
}

static void test_pid_perfect_control(void **state) {
    // test with a perfect control, i.e. all history at setpoint
    // (default initialization) and the current process value at the
    // setpoint. The control output should be zero.
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 1.0f;
    float Ki = 2.0f;
    float Kd = 3.0f;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);

    float value = setpoint;
    float delta_time = 1.0f;
    float control = pid_control(pid, value, delta_time);
    assert_true(fabs(control) < epsilon);
}


static void test_pid_proportional_positive_only(void **state) {
    // test proportional control only
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 1.5f;
    float Ki = 0.0f;
    float Kd = 0.0f;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);

    float value = 90.0f;
    float delta_time = 1.0f;
    float control = pid_control(pid, value, delta_time);
    float expected = 15.0f;
    assert_true(fabs(control - expected) < epsilon);
}

static void test_pid_proportional_negative_only(void **state) {
    // test proportional control only
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 1.5f;
    float Ki = 0.0f;
    float Kd = 0.0f;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);

    float value = 110.0f;
    float delta_time = 1.0f;
    float control = pid_control(pid, value, delta_time);
    float expected = -15.0f;
    assert_true(fabs(control - expected) < epsilon);
}


static void test_pid_derivative_positive_only(void **state) {
    // test derivative control only
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 0.0f;
    float Ki = 0.0f;
    float Kd = 1.5f;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);

    float value = 110.0f;
    float delta_time = 2.0f;
    float control = pid_control(pid, value, delta_time);
    float expected = 7.5f;
    assert_true(fabs(control - expected) < epsilon);
}

static void test_pid_derivative_negative_only(void **state) {
    // test derivative control only
    pid_data* pid;
    uint8_t hist_size = 5;
    float setpoint = 100.0f;
    float Kp = 0.0f;
    float Ki = 0.0f;
    float Kd = 1.5f;
    pid = pid_init(hist_size, setpoint, Kp, Ki, Kd);

    float value = 90.0f;
    float delta_time = 2.0f;
    float control = pid_control(pid, value, delta_time);
    float expected = -7.5f;
    assert_true(fabs(control - expected) < epsilon);
}

//printf("setpoint = %f  value = %f  control = %f  expected = %f\n", setpoint, value, control, expected);

int main(int argc, char** argv) {

    const struct CMUnitTest tests[] = {
        cmocka_unit_test(test_pid_init),
        cmocka_unit_test(test_pid_free),
        cmocka_unit_test(test_pid_init_values),
        cmocka_unit_test(test_pid_perfect_control),
        cmocka_unit_test(test_pid_proportional_positive_only),
        cmocka_unit_test(test_pid_proportional_negative_only),
        cmocka_unit_test(test_pid_derivative_positive_only),
        cmocka_unit_test(test_pid_derivative_negative_only),
    };
    return cmocka_run_group_tests(tests, NULL, NULL);
}
