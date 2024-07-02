# Assets used on Curve

This repository contains token icons and platform logos used on Curve and any other websites that which to use them:

- Token icons are under [`/images`](https://github.com/curvefi/curve-assets/tree/main/images)
- Platform logos are under [`/platforms`](https://github.com/curvefi/curve-assets/tree/main/platforms)

## Adding a token icon

Everyone can create a pool on Curve. In this repo, everyone can add token icons for tokens contained in Curve pools.
Once a token icon is added to this repository, that token icon will be visible on all Curve websites.

To add a token icon:

1. Choose the right folder: under [`/images`](https://github.com/curvefi/curve-assets/tree/main/images), if the token is on Ethereum, then please choose the `assets` folder. If the token is on any other chain, then please choose the appropriate folder.
2. In that folder, upload the token icon. It **must** be a PNG image, and its dimensions **must** be 200x200. The filename **must** be the token's address, in lowercase.

Example:

- This is a correct filename for the CRV token on Ethereum: `/images/assets/0xd533a949740bb3306d119cc777fa900ba034cd52.png`
- This is NOT a correct filename for the CRV token on Ethereum: `/images/assets/0xD533a949740bb3306d119CC777fa900bA034cd52.png` (filename is not lowercase)
- This is NOT a correct filename for the CRV token on Ethereum: `/images/assets-polygon/0xd533a949740bb3306d119cc777fa900ba034cd52.png` (incorrect folder)
- This is NOT a correct filename for the CRV token on Ethereum: `/images/assets/0xd533a949740bb3306d119cc777fa900ba034cd52.jpg` (incorrect file extension)

Once you've opened a PR, we'll review and merge it. Once the PR is merged, the token icon should show up on all sites within minutes.
