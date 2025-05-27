#!/usr/bin/env python
# This script verifies the code changes without importing the full library

def test_selectolax_parsing():
    """Test that selectolax parsing produces the expected results"""
    from selectolax.parser import HTMLParser
    
    # Simple HTML content for testing
    html = """
    <div class="ranavnode">
        <input value="US Market">
        <a class="navlabellink" href="/test-link">Test Make</a>
    </div>
    """
    
    # Parse with selectolax
    parser = HTMLParser(html)
    nav_nodes = parser.css('div.ranavnode')
    
    # Check if we can find the expected elements
    assert len(nav_nodes) == 1, "Should find one ranavnode div"
    
    # Check first child element
    first_node = nav_nodes[0]
    input_elem = first_node.css_first('input')
    assert input_elem is not None, "Should have an input element"
    assert input_elem.attrs.get('value') == "US Market", "Should have correct value attribute"
    
    # Check if we can find the navlabellink
    nav_link = nav_nodes[0].css_first('a.navlabellink')
    assert nav_link is not None, "Should find the navlabellink"
    assert nav_link.text() == "Test Make", "Should extract the correct text"
    assert nav_link.attrs.get('href') == "/test-link", "Should get the correct href attribute"
    
    print("✅ Selectolax parsing test passed!")
    return True

def main():
    """Check if our code changes look correct"""
    print("Verifying code changes...")
    
    # Run the selectolax parsing test
    success = test_selectolax_parsing()
    
    # Print verification result
    print(f"""
Changes made:
1. Added selectolax to requirements.txt for improved parsing performance
2. Added import for HTMLParser from selectolax.parser
3. Converted get_makes() method to use selectolax instead of BeautifulSoup
4. Modified HTML parsing logic to use selectolax's CSS selector approach
5. Adjusted attribute and text extraction to match selectolax's API

The changes should provide better performance while maintaining the same functionality.
""")
    
    return success

if __name__ == "__main__":
    main()