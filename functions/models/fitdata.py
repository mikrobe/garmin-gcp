from dataclasses import dataclass, fields, asdict

import fitdecode


@dataclass(init=False)
class FitData(object):
    def parse(self, fit_frame: fitdecode.FitDataMessage):
        for field in fields(self):
            name = field.name
            if fit_frame.has_field(name):
                value = fit_frame.get_value(name)
                setattr(self, name, value)
