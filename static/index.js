function addToContent(result) {
  for (var i = 0; i < result.length; i++) {
    mainViewModel.content.push(result[i])
  }
  console.log(mainViewModel.content());
}

mainViewModel.getItems(addToContent);
