function printIt(result) {
  for (var i = 0; i < result.length; i++) {
    navVM.content.push(result[i])
  }
  console.log(navVM.content());
}

getItems(printIt);
