#include <SerialTransfer.h>

#define DEBUG_PORT    Serial  //COM12
#define FEEDBACK_PORT Serial2 //COM10


SerialTransfer feedback;


struct __attribute__((__packed__)) state{
  float roll   = 0;
  float pitch  = 0;
  uint16_t hdg = 0;
  uint16_t alt = 0;
  uint16_t ias = 0;
  float lat    = 0;
  float lon    = 0;
  byte flaps   = 0;
  byte gear    = 0;
} plane;


void setup()
{
  DEBUG_PORT.begin(115200);
  FEEDBACK_PORT.begin(115200);
  
  feedback.begin(FEEDBACK_PORT);
}

void loop()
{
  if(feedback.available())
  {
    feedback.rxObj(plane);

    DEBUG_PORT.print("Roll: ");           DEBUG_PORT.println(plane.roll);
    DEBUG_PORT.print("Pitch: ");          DEBUG_PORT.println(plane.pitch);
    DEBUG_PORT.print("Heading: ");        DEBUG_PORT.println(plane.hdg);
    DEBUG_PORT.print("Altitude (m): ");   DEBUG_PORT.println(plane.alt);
    DEBUG_PORT.print("IAS (km/h): ");     DEBUG_PORT.println(plane.ias);
    DEBUG_PORT.print("Latitude (dd): ");  DEBUG_PORT.println(plane.lat);
    DEBUG_PORT.print("Longitude (dd): "); DEBUG_PORT.println(plane.lon);
    DEBUG_PORT.print("Flap State: ");     DEBUG_PORT.println(plane.flaps);
    DEBUG_PORT.print("Gear State: ");     DEBUG_PORT.println(plane.gear);
    DEBUG_PORT.println();
  }
}
