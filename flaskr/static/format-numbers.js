const wholeNumbers = document.querySelectorAll('.whole-number')
const realNumbers = document.querySelectorAll('.real-number')

const realNumbersFormatter = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 2,
  minimumFractionDigits: 2,
})

const wholeNumbersFormatter = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 0,
  minimumFractionDigits: 0,
})

for (const num of realNumbers) {
  num.textContent = realNumbersFormatter.format(parseFloat(num.textContent.trim()))
}

for (const num of wholeNumbers) {
  num.textContent = wholeNumbersFormatter.format(parseFloat(num.textContent.trim()))
}