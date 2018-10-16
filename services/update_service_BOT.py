from odoo.addons.currency_rate_update.services.currency_getter_interface import CurrencyGetterInterface
from datetime import datetime
import urllib.request
import csv
import io

import logging
_logger = logging.getLogger(__name__)


class BOTGetter(CurrencyGetterInterface):
    """Implementation of Currency_getter_factory interface
    for BOT service
    """
    code = 'BOT'
    name = 'Taiwan Of Bank'
    supported_currency_array = [
        "USD", "HKD", "GBP" , "AUD" , "CAD", "SGD", "CHF", "JPY", "ZAR", "SEK",
        "NZD", "THB", "PHP" , "IDR" , "EUR", "KRW", "VND" , "MYR" , "CNY"]

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        url = 'http://rate.bot.com.tw/xrt/flcsv/0/day'

        # We do not want to update the main currency
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        _logger.debug("BOT currency rate service : connecting...")
        try:
            url_open = urllib.request.urlopen(url)
            csvfile = csv.reader(io.StringIO(url_open.read().decode('utf-8-sig')), delimiter=',')
            url_open.close()
        except IOError:
            raise UserError(
                _('Web Service does not exist (%s)!') % url)

        next(csvfile)
        exchange = {}
        for row in csvfile:
            bid = float(row[3])
            ask = float(row[13])

            exchange[row[0]] = {
                'bid': bid,
                'ask': ask
            }

        self.check_rate_date(datetime.today(), max_delta_days)
        self.supported_currency_array = list(exchange.keys())

        self.supported_currency_array.append('TWD')
        _logger.debug("Supported currencies = %s " %
                      self.supported_currency_array)
        self.validate_cur(main_currency)
        if main_currency != 'TWD':
            main_rate = float(exchange[main_currency]['ask'])
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'TWD':
                rate = main_rate
            else:
                if main_currency == 'TWD':
                    rate = 1 / float(exchange[curr]['ask'])
                else:
                    rate = main_rate / float(exchange[curr]['ask'])
            self.updated_currency[curr] = rate
            _logger.debug(
                "Rate retrieved : 1 %s = %s %s" % (main_currency, rate, curr)
            )
        return self.updated_currency, self.log_info