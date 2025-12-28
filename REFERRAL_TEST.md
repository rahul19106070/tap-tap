# Referral System Test Guide

## How the Referral System Works

### 1. **Getting Your Referral Code**
- Open the Mini App
- Go to "Refer" tab
- Your unique referral code is displayed
- Click "Share Referral Link" to copy it

### 2. **Sharing Your Referral Link**
- Format: `https://t.me/your_bot?start=YOUR_REFERRAL_CODE`
- Share this link with friends
- When they click and join, you get 5 coins!

### 3. **How Referrals Are Tracked**

**Via Bot (`/start` command):**
- User clicks referral link: `https://t.me/bot?start=ABC123`
- Bot receives `/start ABC123`
- Bot checks if user exists
- If new user, assigns them to referrer
- Referrer gets 5 coins bonus

**Via Mini App:**
- User opens Mini App with referral code in URL
- Mini App API processes referral
- Same logic applies

### 4. **Testing the Referral System**

#### Test 1: Get Referral Code
1. Open Mini App
2. Navigate to "Refer" tab
3. Verify referral code is displayed
4. Verify referral count shows 0 (if no referrals yet)

#### Test 2: Share Referral Link
1. Click "Share Referral Link" button
2. Link should be copied to clipboard
3. Link format: `https://t.me/your_bot?start=REFERRAL_CODE`

#### Test 3: Test Referral (Using Bot)
1. Get your referral code from Mini App
2. Send `/start YOUR_REFERRAL_CODE` to bot in Telegram
3. Bot should:
   - Create new user
   - Link them to you as referrer
   - Give you 5 coins
   - Send you notification

#### Test 4: Test Referral (Using Mini App)
1. Get referral link
2. Open link in new Telegram account
3. Mini App should open
4. Referrer should get 5 coins

### 5. **Common Issues Fixed**

✅ **Fixed:** `telegram_id=undefined` error
- Added validation to check if user exists before loading referral
- Added error handling for undefined values

✅ **Fixed:** Referral not processing in Mini App
- Added referral code processing in `/api/user` endpoint
- Checks `start_param` from Telegram WebApp initData

✅ **Fixed:** Error handling
- Better error messages
- Validation for invalid telegram_id

### 6. **Database Structure**

**User Table:**
- `referral_code`: Unique code for each user
- `referred_by`: ID of user who referred them (null if none)

**Transaction Table:**
- Records referral bonuses as `referral_bonus` type
- Amount: 5.0 coins
- Description: "Referred user [name]"

### 7. **Verification Checklist**

- [ ] Referral code is generated for new users
- [ ] Referral code is unique
- [ ] Referral link is properly formatted
- [ ] Referrer gets 5 coins when someone joins
- [ ] Referral count updates correctly
- [ ] User can only be referred once
- [ ] Self-referral is prevented
- [ ] Works via bot `/start` command
- [ ] Works via Mini App link

### 8. **API Endpoints**

**GET `/api/referral?telegram_id=123456789`**
- Returns: referral_code, referrals_count, bonus_per_referral
- Error handling for invalid/undefined telegram_id

**POST `/api/user`**
- Processes referral code from `start_param`
- Creates user and links to referrer if code provided

### 9. **Bot Commands**

**`/start REFERRAL_CODE`**
- Handles referral when user starts bot
- Gives bonus to referrer

**`/referral`**
- Shows user's referral link
- Displays referral stats

