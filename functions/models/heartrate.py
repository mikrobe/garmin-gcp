class HeartRate(object):

    def __init__(self, daily_heart_rate_data):
        self.daily_heart_rate_data = daily_heart_rate_data

    def heart_rate_values(self):
        heart_rate_value_descriptors = self.daily_heart_rate_data["heartRateValueDescriptors"]
        timestamp_index = self._get_value_index(heart_rate_value_descriptors, "timestamp")
        heart_rate_index = self._get_value_index(heart_rate_value_descriptors, "heartrate")

        heart_rate_values = self.daily_heart_rate_data["heartRateValues"]

        def map_value(x):
            return {
                "timestamp": int(x[timestamp_index] / 1000),
                "heart_rate": x[heart_rate_index]
            }

        return list(
            map(lambda x: map_value(x), heart_rate_values)
        )

    def _get_value_index(self, heart_rate_value_descriptors, key):
        return next(
            map(lambda x: x["index"],
                filter(lambda x: x["key"] == key, heart_rate_value_descriptors)
                )
        )
