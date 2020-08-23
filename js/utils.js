function parse_cookies(cookies) {
    let res = {};

    let cookies_list = cookies.split('; ');
    for (let i = 0; i < cookies_list.length; ++i) {
        let tmp = cookies_list[i].split('=');
        let key = tmp[0];
        let val = tmp[1];
        res[key] = val;
    }
    return res;
}

export{parse_cookies}
