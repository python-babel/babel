#include <iostream>
#include <sstream>
#include <unicode/smpdtfmt.h>
#include <unicode/timezone.h>

static std::vector<std::string> split(const std::string &s, char delimiter) {
  std::vector<std::string> tokens;
  std::string token;
  std::istringstream tokenStream(s);
  while (std::getline(tokenStream, token, delimiter)) {
    tokens.push_back(token);
  }
  return tokens;
}

static UDate parse_time_str(const char *time_str) {
  UErrorCode status = U_ZERO_ERROR;
  icu::UnicodeString fauxISO8601("yyyy-MM-dd'T'hh:mm:ss'Z'");
  auto fmt = new icu::SimpleDateFormat(fauxISO8601, status);
  fmt->setTimeZone(*icu::TimeZone::getGMT());
  UDate date = fmt->parse(icu::UnicodeString(time_str), status);
  if (U_FAILURE(status)) {
    std::cerr << "Failed to parse time string: " << time_str << std::endl;
    exit(1);
  }
  return date;
}

static std::vector<icu::Locale> parse_locales(const char *locales_str) {
  auto locales = std::vector<icu::Locale>{};
  for (auto token : split(locales_str, ',')) {
    auto loc = icu::Locale(token.c_str());
    if (loc.isBogus()) {
      std::cerr << "Invalid locale: " << token << std::endl;
      exit(1);
    }
    locales.push_back(loc);
  }
  return locales;
}

static std::vector<icu::TimeZone *> parse_timezones(const char *timezones_str) {
  auto timezones = std::vector<icu::TimeZone *>{};
  for (auto token : split(timezones_str, ',')) {
    auto tz = icu::TimeZone::createTimeZone(token.c_str());
    if (tz == nullptr) {
      std::cerr << "Invalid timezone: " << token << std::endl;
      exit(1);
    }
    timezones.push_back(tz);
  }
  return timezones;
}

int main() {
  UErrorCode status = U_ZERO_ERROR;
  const char *timezones_str = getenv("TEST_TIMEZONES");
  const char *locales_str = getenv("TEST_LOCALES");
  const char *time_str = getenv("TEST_TIME");
  const char *time_format_str = getenv("TEST_TIME_FORMAT");

  if (!timezones_str || !locales_str) {
    std::cerr << "Please set TEST_TIMEZONES, TEST_LOCALES environment variables"
              << std::endl;
    return 1;
  }

  if (time_str == nullptr) {
    time_str = "2025-03-04T13:53:00Z";
    std::cerr << "Defaulting TEST_TIME to " << time_str << std::endl;
  }

  if (time_format_str == nullptr) {
    time_format_str = "z:zz:zzz:zzzz";
    std::cerr << "Defaulting TEST_TIME_FORMAT to " << time_format_str
              << std::endl;
  }

  auto date = parse_time_str(time_str);
  auto timezones = parse_timezones(timezones_str);
  auto locales = parse_locales(locales_str);

  for (auto tz : timezones) {
    icu::UnicodeString tzid;
    tz->getID(tzid);
    std::string tzid_str;
    tzid.toUTF8String(tzid_str);
    for (auto loc : locales) {
      auto fmt = new icu::SimpleDateFormat(time_format_str, loc, status);
      fmt->setTimeZone(*tz);
      icu::UnicodeString name;
      fmt->format(date, name);
      std::string result;
      name.toUTF8String(result);
      std::cout << tzid_str << "\t" << loc.getName() << "\t" << result
                << std::endl;
      delete fmt;
    }
  }
  return 0;
}
