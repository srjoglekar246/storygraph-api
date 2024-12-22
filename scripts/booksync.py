import argparse
import sys
from storygraph_api.users_client import User
from storygraph_api.auth_util import get_user_token_cookie

def main():
    if sys.platform != 'darwin':
        raise EnvironmentError("This script is only supported on MacOS")

    parser = argparse.ArgumentParser(description='Get books read by a user from StoryGraph.')
    parser.add_argument('uname', type=str, help='Username of the user')
    
    args = parser.parse_args()
    
    cookie = get_user_token_cookie()
    print(f"Cookie: {cookie}")
    
    user = User()
    books_read = user.books_read(args.uname, cookie)
    print(books_read)

if __name__ == '__main__':
    main()