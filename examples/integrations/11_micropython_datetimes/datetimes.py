from puepy import Application, Page, t
import datetime

app = Application()


@app.page()
class DatetimesPage(Page):
    def populate(self):
        import js

        browser_utc_offset = js.Date.new().getTimezoneOffset()

        browser_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(minutes=browser_utc_offset)))
        utc_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=0)))

        t.h1("Hello, World!")
        with t.ul():
            t.li(f"Browser UTC offset: {browser_utc_offset} minutes")
            t.li(f"Browser time: {browser_time}")
            t.li(f"UTC time: {utc_time}")


app.mount("#app")
