from enum import Enum

class GqlRequestEnum(Enum):
    search = (
        """
        query ($search: String) {
          Media (search: $search) {
            id
            title {
              english
            }
          }
        }
        """
    )