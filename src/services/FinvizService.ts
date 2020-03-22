const JSSoup = require("jssoup").default;
const fetch = require("node-fetch");

export default class FinvizTicker {
    public static ticker: string;
    public static url: string;
    public metrics: any;
    constructor(ticker: string) {
        FinvizTicker.ticker = ticker.toUpperCase();
        FinvizTicker.url =
            "http://finviz.com/quote.ashx?t=" + FinvizTicker.ticker;
    }
    public async setMetrics() {
        let metrics: any = {};

        const body = await fetch(FinvizTicker.url)
            .then((res: any) => res.text())
            .then((body: any) => body);

        if (
            body.includes(
                "We cover only stocks and ETFs listed on NYSE, NASDAQ, and AMEX. International and OTC/PK are not available."
            )
        ) {
            throw new Error(
                "Stock ticker '" +
                    FinvizTicker.ticker +
                    "' does not exist on the Finviz."
            );
        }

        const soup = new JSSoup(body);

        // Extract the main table with ticker data and create a list of the rows in the table
        const table = soup.find("table", { class: "snapshot-table2" });
        const rows = table.findAll("tr");

        // Loop through the rows and build a dictionary of the elements
        rows.forEach((row: any) => {
            // Extracts the columns of each row
            const cols = row.findAll("td");

            // Check if there is an even number of columns (should always be)
            if (cols.length % 2 == 0) {
                const colTexts = cols.map((col: any) => col.text);
                const keys = colTexts
                    .filter((colText: any, index: number) => index % 2 === 0)
                    .map((key: any) => key.toString());
                const values = colTexts
                    .filter((colText: any, index: number) => index % 2 !== 0)
                    .map((value: any) => value.toString());
                const keyValuePairs = keys.map(function(
                    key: string,
                    index: number
                ) {
                    return [key, values[index]];
                });
                keyValuePairs.forEach((keyValue: Array<string>) => {
                    metrics[keyValue[0]] = keyValue[1];
                });
                this.metrics = metrics;
            } else {
                throw new Error(
                    "Dude, the Finviz table doesn't have an even number of columns!"
                );
            }
        });
    }
}
