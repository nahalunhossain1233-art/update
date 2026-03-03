import asyncio
import os
import sys
import random
from playwright.async_api import async_playwright

# CRITICAL FIX FOR WINDOWS: Set the correct event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class KlarnaAutomation:
    def __init__(self, num_tabs, delay_seconds):
        self.numbers_file = "numbers.txt"
        self.running = True
        self.num_tabs = num_tabs
        self.delay_seconds = delay_seconds
    
    def human_delay(self, min_seconds=0.3, max_seconds=1.2):
        """Create random human-like delays"""
        return random.uniform(min_seconds, max_seconds)
    
    def human_typing_delay(self):
        """Simulate human typing speed with random delays between keystrokes"""
        return random.uniform(0.1, 0.3)
    
    def get_next_number(self):
        """Get next number from file and remove it"""
        if not os.path.exists(self.numbers_file):
            print(f"❌ Error: {self.numbers_file} not found!")
            return None
        
        try:
            with open(self.numbers_file, 'r') as f:
                numbers = f.read().strip().split('\n')
            
            # Filter out empty lines
            numbers = [n.strip() for n in numbers if n.strip()]
            
            if not numbers:
                print("❌ Error: No numbers found in file!")
                return None
            
            next_number = numbers[0]
            
            # Remove the used number
            with open(self.numbers_file, 'w') as f:
                f.write('\n'.join(numbers[1:]))
            
            return next_number
            
        except Exception as e:
            print(f"❌ Error reading numbers file: {e}")
            return None
    
    async def human_type(self, page, selector, text):
        """Type like a human with random delays between keystrokes"""
        await page.click(selector)  # Click to focus
        await asyncio.sleep(self.human_delay(0.2, 0.4))
        
        # Clear field first
        await page.fill(selector, "")
        await asyncio.sleep(self.human_delay(0.1, 0.2))
        
        # Type character by character with human-like delays
        for char in text:
            await page.type(selector, char, delay=self.human_typing_delay() * 1000)  # Convert to ms
            # Random occasional longer pause between words or numbers
            if char in [' ', '@', '.', '-'] or random.random() < 0.1:  # 10% chance of pause
                await asyncio.sleep(self.human_delay(0.2, 0.5))
        
        # Small pause after typing
        await asyncio.sleep(self.human_delay(0.3, 0.6))
    
    async def random_mouse_movement(self, page):
        """Simulate random mouse movements"""
        try:
            viewport_size = await page.evaluate('''() => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            }''')
            
            # Random mouse movement to a random position
            x = random.randint(100, viewport_size['width'] - 100)
            y = random.randint(100, viewport_size['height'] - 100)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(self.human_delay(0.1, 0.3))
        except:
            pass  # Ignore if mouse movement fails
    
    async def handle_tab(self, page, tab_id):
        """Handle automation for a single tab with human-like behavior"""
        try:
            # Navigate to login page with timeout handling
            print(f"📌 Tab {tab_id}: Loading Klarna...")
            try:
                await page.goto(
                    "https://app.klarna.com/login?auto-login&market=DE&locale=de-DE", 
                    wait_until="domcontentloaded",
                    timeout=30000
                )
                print(f"✅ Tab {tab_id}: Page loaded")
                
                # Random initial delay like human reading the page
                await asyncio.sleep(self.human_delay(1.5, 3.0))
                
            except Exception as e:
                print(f"⚠️ Tab {tab_id}: Navigation issue: {e}")
                await page.reload(timeout=30000)
                await asyncio.sleep(self.human_delay(2.0, 4.0))
            
            while self.running:
                # Get next number for this iteration
                phone_number = self.get_next_number()
                if not phone_number:
                    print(f"⏹️ Tab {tab_id}: No more numbers available")
                    break
                
                print(f"\n🔄 Tab {tab_id}: Processing: {phone_number}")
                
                try:
                    # Random mouse movement before interaction
                    await self.random_mouse_movement(page)
                    
                    # STEP 1: Fill phone number (HUMAN-LIKE TYPING)
                    print(f"📝 Tab {tab_id}: Step 1/7 - Typing phone number...")
                    await page.wait_for_selector('input[name="emailOrPhone"]', timeout=15000)
                    
                    # Human-like typing with random delays
                    await self.human_type(page, 'input[name="emailOrPhone"]', phone_number)
                    print(f"✅ Tab {tab_id}: Phone number entered")
                    
                    # Random pause after filling
                    await asyncio.sleep(self.human_delay(0.5, 1.5))
                    
                    # Random mouse movement before clicking
                    await self.random_mouse_movement(page)
                    
                    # STEP 2: Click Continue button (Weiter)
                    print(f"📝 Tab {tab_id}: Step 2/7 - Moving to Continue button...")
                    
                    # Hover over button first (human-like)
                    continue_button = await page.wait_for_selector('span[id="onContinue__text"]', timeout=5000)
                    await continue_button.hover()
                    await asyncio.sleep(self.human_delay(0.2, 0.5))
                    
                    # Click with random delay
                    await continue_button.click()
                    print(f"✅ Tab {tab_id}: Clicked Continue")
                    
                    # Random pause after clicking
                    await asyncio.sleep(self.human_delay(0.8, 1.8))
                    
                    # STEP 3: Wait for user-specified delay
                    print(f"⏳ Tab {tab_id}: Step 3/7 - Waiting {self.delay_seconds} seconds...")
                    
                    # During the wait, simulate some random activity
                    for i in range(self.delay_seconds // 5):  # Break into 5-second chunks
                        await asyncio.sleep(5)
                        # Random mouse movement every 5 seconds to look active
                        if random.random() < 0.3:  # 30% chance
                            await self.random_mouse_movement(page)
                            print(f"👆 Tab {tab_id}: Small mouse movement")
                    
                    # Handle remaining seconds if not divisible by 5
                    remaining = self.delay_seconds % 5
                    if remaining > 0:
                        await asyncio.sleep(remaining)
                    
                    # STEP 4: Click Resend Code button (SECOND-LAST BUTTON)
                    print(f"📝 Tab {tab_id}: Step 4/7 - Moving to Resend Code button...")
                    
                    # Wait for button and hover first
                    resend_button = await page.wait_for_selector('span[id="btn_resend_code__text"]', timeout=10000)
                    await resend_button.hover()
                    await asyncio.sleep(self.human_delay(0.3, 0.7))
                    
                    # Click
                    await resend_button.click()
                    print(f"✅ Tab {tab_id}: Clicked Resend Code")
                    
                    # STEP 5: Wait 2 seconds after clicking Resend (HUMAN PAUSE)
                    print(f"⏳ Tab {tab_id}: Step 5/7 - Waiting 2 seconds...")
                    await asyncio.sleep(2)
                    
                    # Random mouse movement
                    await self.random_mouse_movement(page)
                    
                    # STEP 6: Click Change link (LAST BUTTON)
                    print(f"📝 Tab {tab_id}: Step 6/7 - Moving to Change link...")
                    
                    # Hover over link first
                    change_link = await page.wait_for_selector('a.kaf-action-link:has-text("Ändern")', timeout=5000)
                    await change_link.hover()
                    await asyncio.sleep(self.human_delay(0.2, 0.5))
                    
                    # Click
                    await change_link.click()
                    print(f"✅ Tab {tab_id}: Clicked Change link")
                    
                    # STEP 7: Wait for form to reset before next cycle
                    print(f"⏳ Tab {tab_id}: Step 7/7 - Preparing for next cycle...")
                    await asyncio.sleep(self.human_delay(1.5, 3.0))
                    
                    # Random longer pause between cycles
                    if random.random() < 0.3:  # 30% chance of extra pause
                        extra_pause = random.uniform(1.0, 2.5)
                        print(f"⏱️ Tab {tab_id}: Extra human pause for {extra_pause:.1f} seconds...")
                        await asyncio.sleep(extra_pause)
                    
                    print(f"✅ Tab {tab_id}: Complete cycle finished for {phone_number}")
                    print(f"🔄 Tab {tab_id}: Ready for next number\n")
                    
                except Exception as e:
                    print(f"❌ Tab {tab_id}: Error: {e}")
                    # Try to recover by refreshing like a human would
                    try:
                        print(f"🔄 Tab {tab_id}: Refreshing page...")
                        await page.reload(timeout=30000)
                        await asyncio.sleep(self.human_delay(3.0, 5.0))
                    except:
                        pass
                    
        except Exception as e:
            print(f"💥 Tab {tab_id}: Fatal error: {e}")
    
    async def run(self):
        """Main execution function"""
        # Check if numbers file exists and has content
        if not os.path.exists(self.numbers_file):
            print(f"❌ Error: {self.numbers_file} not found! Exiting.")
            input("Press Enter to exit...")
            return
        
        with open(self.numbers_file, 'r') as f:
            content = f.read().strip()
            if not content:
                print("❌ Error: numbers.txt is empty! Exiting.")
                input("Press Enter to exit...")
                return
        
        print("="*80)
        print("🚀 STARTING KLARNA AUTOMATION - HUMANIZED MODE")
        print("="*80)
        print(f"📋 Configuration:")
        print(f"   • Number of tabs: {self.num_tabs}")
        print(f"   • Main delay: {self.delay_seconds} seconds")
        print(f"   • Numbers file: {self.numbers_file}")
        print("="*80)
        print("📋 Workflow per tab (HUMAN-LIKE BEHAVIOR):")
        print("   1. Type phone number with human-like delays")
        print("   2. Hover then click Continue")
        print(f"   3. Wait {self.delay_seconds} seconds (with random mouse movements)")
        print("   4. Hover then click Resend Code")
        print("   5. Wait 2 seconds")
        print("   6. Hover then click Change link")
        print("   7. Random human pauses throughout")
        print("   8. REPEAT with next number")
        print("="*80)
        
        async with async_playwright() as p:
            # Launch browser with Windows-specific arguments
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-web-security',
                    '--disable-features=BlockInsecurePrivateNetworkRequests',
                    '--start-maximized',
                ]
            )
            
            # Create a single browser context with realistic viewport
            context = await browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='de-DE',
                timezone_id='Europe/Berlin'
            )
            
            # Create tabs in the SAME window based on user input
            tabs = []
            print(f"\n📑 Creating {self.num_tabs} tabs in ONE window...")
            for i in range(self.num_tabs):
                page = await context.new_page()
                tabs.append(page)
                print(f"  ✓ Tab {i+1} created")
            
            print("\n" + "="*80)
            print(f"✅ SUCCESS: 1 browser window with {self.num_tabs} tabs")
            print(f"   ⚠️  Look for a SINGLE browser window with {self.num_tabs} tabs")
            print(f"   🤖 Bot detection evasion: ACTIVE")
            print(f"   ⏱️  Main delay: {self.delay_seconds} seconds")
            print("="*80 + "\n")
            
            # Random initial delay before starting
            initial_delay = random.uniform(1.0, 3.0)
            print(f"⏱️ Initial human-like delay: {initial_delay:.1f} seconds...")
            await asyncio.sleep(initial_delay)
            
            # Run all tabs concurrently
            tasks = []
            for i, page in enumerate(tabs):
                task = asyncio.create_task(self.handle_tab(page, i + 1))
                tasks.append(task)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Close browser
            print("\n📦 Closing browser...")
            await browser.close()
            print("✅ Automation completed!")
            print("="*80)
            input("Press Enter to exit...")

def get_user_input():
    """Get user input for number of tabs and delay time"""
    print("="*80)
    print("🔧 KLARNA AUTOMATION - SETUP")
    print("="*80)
    
    # Get number of tabs
    while True:
        try:
            num_tabs = int(input("📑 Enter number of tabs to open (1-10): "))
            if 1 <= num_tabs <= 10:
                break
            else:
                print("❌ Please enter a number between 1 and 10")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Get delay time
    while True:
        try:
            delay = int(input("⏱️  Enter main delay time in seconds (10-120): "))
            if 10 <= delay <= 120:
                break
            else:
                print("❌ Please enter a number between 10 and 120")
        except ValueError:
            print("❌ Please enter a valid number")
    
    print("="*80)
    return num_tabs, delay

async def main():
    # Get user input
    num_tabs, delay = get_user_input()
    
    # Create automation instance with user settings
    automation = KlarnaAutomation(num_tabs, delay)
    await automation.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Automation stopped by user")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        input("Press Enter to exit...")
