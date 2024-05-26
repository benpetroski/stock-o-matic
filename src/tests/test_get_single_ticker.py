import unittest
import json
import os
from datetime import datetime

tickerToTest = 'ZZZ'

class TestGetSingleTicker(unittest.TestCase):

    def setUp(self):
        # delete the JSON file if it exists
        if os.path.exists('data/tickers/'+ tickerToTest + '.json'):
            os.remove('data/tickers/'+ tickerToTest + '.json')

        # Run the script to generate the JSON file
        os.system('python3 get_single_ticker.py ' + tickerToTest)

    def test_json_file(self):
        file_path = 'data/tickers/' + tickerToTest + '.json'
        self.assertTrue(os.path.exists(file_path), f"{file_path} does not exist")

        with open(file_path, 'r') as f:
            data = json.load(f)

        # Define the expected keys and their types
        expected_keys = {
            "Sector": str,
            "Industry": str,
            "Country": str,
            "Exchange": str,
            "Index": str,
            "PE": str,
            "EPSttm": str,
            "InsiderOwn": str,
            "ShsOutstand": float,
            "PerfWeek": str,
            "LastUpdated": str,
            "MarketCap": float,
            "ForwardPE": str,
            "EPSnextY": str,
            "InsiderTrans": str,
            "ShsFloat": float,
            "PerfMonth": str,
            "Income": float,
            "PEG": str,
            "EPSnextQ": str,
            "InstOwn": str,
            "ShortFloat": str,
            "PerfQuarter": str,
            "Sales": float,
            "PS": str,
            "EPSthisY": str,
            "InstTrans": str,
            "ShortRatio": str,
            "PerfHalfY": str,
            "Booksh": str,
            "PB": str,
            "ROA": str,
            "ShortInterest": float,
            "PerfYear": str,
            "Cashsh": str,
            "PC": str,
            "EPSnext5Y": str,
            "ROE": str,
            "FiftyTwoWRange": list,
            "PerfYTD": str,
            "DividendEst": list,
            "PFCF": str,
            "EPSpast5Y": str,
            "ROI": str,
            "FiftyTwoWHigh": str,
            "Beta": str,
            "DividendTTM": list,
            "QuickRatio": str,
            "Salespast5Y": str,
            "GrossMargin": str,
            "FiftyTwoWLow": str,
            "ATR14": str,
            "DividendEx-Date": str,
            "CurrentRatio": str,
            "EPSYYTTM": str,
            "OperMargin": str,
            "RSI14": str,
            "Volatility": list,
            "Employees": str,
            "DebtEq": str,
            "SalesYYTTM": str,
            "ProfitMargin": str,
            "Recom": str,
            "TargetPrice": str,
            "OptionShort": bool,
            "LTDebtEq": str,
            "EPSQQ": str,
            "Payout": str,
            "RelVolume": str,
            "PrevClose": str,
            "SalesSurprise": str,
            "EPSSurprise": str,
            "SalesQQ": str,
            "Earnings": str,
            "AvgVolume": float,
            "Price": str,
            "SMA20": str,
            "SMA50": str,
            "SMA200": str,
            "Trades": str,
            "Volume": str,
            "Change": str
        }

        # Check all expected keys and types
        for key, expected_type in expected_keys.items():
            self.assertIn(key, data, f"Missing key: {key}")
            self.assertIsInstance(data[key], expected_type, f"Incorrect type for key: {key}")
            if expected_type in [str, list]:
                self.assertTrue(data[key], f"Value for key {key} should not be empty")
            elif expected_type == float:
                self.assertNotEqual(data[key], 0, f"Value for key {key} should not be zero")

        # Additional check for 'LastUpdated' format (YYYY-MM-DD)
        try:
            datetime.strptime(data['LastUpdated'], '%Y-%m-%d')
        except ValueError:
            self.fail("LastUpdated date format is incorrect")

if __name__ == '__main__':
    unittest.main()
