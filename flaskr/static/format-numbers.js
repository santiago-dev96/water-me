const wholeNumbers = document.querySelectorAll('.whole-number')
const realNumbers = document.querySelectorAll('.real-number')

for (const num of realNumbers) {
const formatter = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
})
num.textContent = formatter.format(parseFloat(num.textContent.trim()))
}

for (const num of wholeNumbers) {
const formatter = new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
})
num.textContent = formatter.format(parseFloat(num.textContent.trim()))
}