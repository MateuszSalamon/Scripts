//IMUCompensation

#include <iostream>

#include <cmath>
#include <iostream>

struct Quaternion {
    double w, x, y, z;
};

struct Vector3 {
    double x, y, z;
};

struct PYR_values
{
  double roll,pitch,yaw, accuracyRoll, accuracyPitch, accuracyYaw;
};

Quaternion orientation;

void processUbloxAttitude(int32_t raw_roll, int32_t raw_pitch, int32_t raw_heading);

Quaternion toQuaternion(double roll_rad, double pitch_rad, double yaw_rad) {
    // Abbreviations for the various angular functions
    double cr = cos(roll_rad * 0.5);
    double sr = sin(roll_rad * 0.5);
    double cp = cos(pitch_rad * 0.5);
    double sp = sin(pitch_rad * 0.5);
    double cy = cos(yaw_rad * 0.5);
    double sy = sin(yaw_rad * 0.5);

    Quaternion q;
    q.w = cr * cp * cy + sr * sp * sy;
    q.x = sr * cp * cy - cr * sp * sy;
    q.y = cr * sp * cy + sr * cp * sy;
    q.z = cr * cp * sy - sr * sp * cy;
/*
w = \cos(\phi/2)\cos(\theta/2)\cos(\psi/2) + \sin(\phi/2)\sin(\theta/2)\sin(\psi/2)
x = \sin(\phi/2)\cos(\theta/2)\cos(\psi/2) - \cos(\phi/2)\sin(\theta/2)\sin(\psi/2)
y = \cos(\phi/2)\sin(\theta/2)\cos(\psi/2) + \sin(\phi/2)\cos(\theta/2)\sin(\psi/2)
z = \cos(\phi/2)\cos(\theta/2)\sin(\psi/2) - \sin(\phi/2)\sin(\theta/2)\cos(\psi/2)
*/
    return q;
}

void feedMeUBX_NAV_ATT(PYR_values pyr)
{
  processUbloxAttitude(pyr.roll, pyr.pitch, pyr.yaw);
}

// Usage with UBX-NAV-ATT data
void processUbloxAttitude(int32_t raw_roll, int32_t raw_pitch, int32_t raw_heading) {
    const double DEG_TO_RAD = M_PI / 180.0;
    const double SCALE = 1e-5;

    double roll  = (raw_roll * SCALE) * DEG_TO_RAD;
    double pitch = (raw_pitch * SCALE) * DEG_TO_RAD;
    double yaw   = (raw_heading * SCALE) * DEG_TO_RAD;

    //Quaternion orientation = toQuaternion(roll, pitch, yaw);
    orientation = toQuaternion(roll, pitch, yaw);
    
    std::cout << "Quaternion: w=" << orientation.w << " x=" << orientation.x <<" y="<<orientation.y<<" z="<<orientation.z<< std::endl;
}

// Function to isolate true linear acceleration
Vector3 getLinearAcceleration(const Quaternion& q, const Vector3& raw_accel) {
    // 1. Define standard gravity (assuming raw_accel is in m/s^2)
    // If your raw_accel is in "g"s, set this to 1.0 instead.
    const double G = 9.80665; 
    
    // 2. Calculate the expected gravity vector in the sensor's local frame
    Vector3 expected_gravity;
    expected_gravity.x = 2.0 * (q.x * q.z - q.w * q.y) * G;
    expected_gravity.y = 2.0 * (q.y * q.z + q.w * q.x) * G;
    expected_gravity.z = (q.w * q.w - q.x * q.x - q.y * q.y + q.z * q.z) * G;
    
    // 3. Remove gravity from the raw accelerometer reading
    Vector3 linear_accel;
    
    // NOTE: Depending on how u-blox outputs raw Z (positive or negative at rest),
    // you may need to ADD expected_gravity instead of subtracting. 
    // Test this by leaving the device flat and motionless; linear_accel should be near [0, 0, 0].
    linear_accel.x = raw_accel.x - expected_gravity.x;
    linear_accel.y = raw_accel.y - expected_gravity.y;
    linear_accel.z = raw_accel.z - expected_gravity.z;
    
    return linear_accel;
}

int main() {
    // Example: Device pitched up 90 degrees (standing on its tail)
    // In this state, gravity should fully act on the X-axis.
    Quaternion my_orientation = {0.7071, 0.0, 0.7071, 0.0}; // 90 deg pitch
    Vector3 raw_sensor_data = {-9.81, 5.1, 2.0};            // Feeling 1g on X
    PYR_values pyr {.roll = 2.1, .pitch = 3.2, .yaw = 4.3, .accuracyRoll = 0.41, .accuracyPitch = 0.72, .accuracyYaw = 0.5}
    feedMeUBX_NAV_ATT(pyr);
    //use a sideeffect for now
    //Vector3 pure_motion = getLinearAcceleration(my_orientation, raw_sensor_data);
    Vector3 pure_motion = getLinearAcceleration(orientation, raw_sensor_data);

    std::cout << "Linear Accel X: " << pure_motion.x << "\n";
    std::cout << "Linear Accel Y: " << pure_motion.y << "\n";
    std::cout << "Linear Accel Z: " << pure_motion.z << "\n";

    return 0;
}
