/*
   This file is part of VISP Core.

   VISP Core is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   VISP Core is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with VISP Core.  If not, see <http://www.gnu.org/licenses/>.

   Author: Steven.Carr@hammontonmakers.org
*/

#ifndef __MOTOR_H__
#define __MOTOR_H__

#define MOTOR_UNKNOWN     0
#define MOTOR_AUTODETECT  1
#define MOTOR_HBRIDGE     2
#define MOTOR_STEPPER     3


extern volatile bool motorFound;

void motorSetup();
bool motorDetectionInProgress(); // calibration cannot happen while we are running motors for detection

typedef void (*motorFunction)();

extern motorFunction motorSpeedUp;
extern motorFunction motorSlowDown;
extern motorFunction motorStop;
extern motorFunction motorGo;
extern motorFunction motorGoHome;
extern motorFunction motorReverseDirection;

extern motorFunction motorRun; // call in loop()

extern int8_t motorType;
extern int8_t motorHomingSpeed; // 0->100 as a percentage
extern int8_t motorMinSpeed;    // 0->100 as a percentage
extern int8_t motorSpeed;       // 0->100 as a percentage
extern int16_t motorStepsPerRev;

// The status of the motor is needed for fault identification
#define MOTOR_STOPPED 0
#define MOTOR_HOMING  1
#define MOTOR_RUNNING 2
extern int8_t motorRunState;

#endif
