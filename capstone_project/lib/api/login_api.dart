import 'api_util.dart' as api;
import 'dart:convert';

/// Makes a request to set Current Orginization
///
/// @param orgData: Object containing all needed information
/// to set orginization: orginization name
/// 
///
/// @return Success if orginization set and the orginization's ID, 
/// Failure if orginization not set: defualts to test organization w/ ID of 0
Future setOrginization(Map orgData) async {
  try {
    var results = await api.post('/setOrginization', orgData);
    return await jsonDecode(results);
  } catch (err) {
    return {"status": "error"};
  }
}

/// Makes request to get all orginization names
///
/// @return Json object with the all orgs
Future getOrgNames() async {
  var results = await api.get('/getOrgNames');
  return jsonDecode(results);
}


/// Makes a request to sign up a new User
///
/// @param userData: Object containing all needed information
/// to sign up a new user: First Name, Last Name, Username, Email, Password
/// 
///
/// @return True if user can now sign in, false if user needs to confirm sign in
/// or error if action failed
Future signUpUser(Map userData) async {
  try {
    var results = await api.post('/signUp', userData);
    return await jsonDecode(results);
  } catch (err) {
    return {"status": "error"};
  }
}

/// Confirms a new user
///
/// @param userConfirmation: Object containing all needed information
/// to confrim User: Username, Confirmation Code
/// 
///
/// @return True if user can now sign in, false if user confirmation failed in
/// or error if action failed
Future confirmSignUp(Map userConfirmation) async {
  try {
    var results = await api.post('/confirmSignUp', userConfirmation);
    return await jsonDecode(results);
  } catch (err) {
    return {"status": "error"};
  }
}

/// User Login
///
/// @param loginCredintials: Object containing all needed information
/// to login: Username, password
/// 
///
/// @return accesstoken for the user
Future logIn(Map loginCredintials) async {
  try {
    var results = await api.post('/signIn', loginCredintials);
    return await jsonDecode(results);
  } catch (err) {
    return {"status": "error"};
  }
}

/// Makes request to get all users
///
/// @return Json object with the all users info
Future getUsers() async {
  var results = await api.get('/getUsers');
  return jsonDecode(results);
}