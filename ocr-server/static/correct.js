send_gt_text =  function (input) {
  // stop the regular form submission

  // collect the form data while iterating over the inputs
  // var data = {};
  // for (var i = 0, ii = form.length; i < ii; ++i) {
  //   var input = form[i];
  //   if (input.name) {
  //     data[input.name] = input.value;
  //   }
  // }
  var data = {};
  data.gt = input.value
  data.id = input.id

  // construct an HTTP request
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/sample', true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');

  // send the collected data as JSON
  // alert(JSON.stringify(data))
  xhr.send(JSON.stringify(data));

  xhr.onloadend = function () {
    // done
  };
};
