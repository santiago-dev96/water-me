const timestamps = document.querySelectorAll('.timestamps')

const formatter = new Intl.DateTimeFormat('en-US', {})

for (const timestamp of timestamps) {
  num.textContent = realNumbersFormatter.format(num.textContent.trim())
}
