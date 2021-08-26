class Logging:
    # Only prints message with debug mode
    def debug(self, message, *args):
        if Prefs['debug']:
            return Log(message, *args)

    # Prints any message you give
    def info(self, message, *args):
        return Log(message, *args)

    # For the below logging:
    # Default level is info
    # Set debug by calling ('sometext', 'debug')

    # Prints a bunch of divider chars like ---
    def separator(self, msg=None, log_level="info"):
        divider = "-" * 35
        output = divider + divider
        # Override output with message if passed
        if msg:
            output = divider + msg + divider

        if log_level.lower() == "debug":
            return self.debug(output)
        return self.info(output)

    # Loops through array of dictionaries and logs them
    def metadata(self, dict_arr, log_level="info"):
        # Loop through dicts in array
        for log_type in dict_arr:
            # Loop through each key/value
            for key, val in log_type.items():
                if val:
                    output = "{key:<20}{val}".format(
                        key=key,
                        val=val
                        )
                    if log_level.lower() == "debug":
                        self.debug(output)
                    else:
                        self.info(output)

    def metadata_arrs(self, dict_arr, log_level="info"):
        # Loop through dicts in array
        for log_type in dict_arr:
            # Loop through each key/value
            for key, val in log_type.items():
                if val:
                    # Loop through dict's array
                    for item in val:
                        output = ("{key:<20}{val}".format(
                            key=key,
                            val=item
                            )
                        )
                        if log_level.lower() == "debug":
                            self.debug(output)
                        else:
                            self.info(output)
