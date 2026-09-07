import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


EXPECTED_CARD_COUNT = 5

# Maps filter value -> tags that should remain visible
FILTER_CASES = [
    ("ai",        ["ai"]),
    ("audio",     ["audio"]),
    ("streaming", ["streaming"]),
    ("social",    ["social"]),
    ("web",       ["web"]),
]


def click_filter(driver, filter_value):
    btn = driver.find_element(By.CSS_SELECTOR, f'.filter-btn[data-filter="{filter_value}"]')
    driver.execute_script("arguments[0].click();", btn)


def visible_cards(driver):
    return [
        c for c in driver.find_elements(By.CSS_SELECTOR, ".project-card")
        if "hidden" not in (c.get_attribute("class") or "")
    ]


class TestProjectCards:
    def test_all_cards_present(self, page):
        cards = page.find_elements(By.CSS_SELECTOR, ".project-card")
        assert len(cards) == EXPECTED_CARD_COUNT

    def test_all_cards_visible_by_default(self, page):
        assert len(visible_cards(page)) == EXPECTED_CARD_COUNT

    def test_each_card_has_title(self, page):
        titles = page.find_elements(By.CSS_SELECTOR, ".card-title")
        assert len(titles) == EXPECTED_CARD_COUNT
        for t in titles:
            assert t.get_attribute("textContent").strip()

    def test_each_card_has_read_more_link(self, page):
        links = page.find_elements(By.CSS_SELECTOR, ".card-read-more")
        assert len(links) == EXPECTED_CARD_COUNT
        for link in links:
            href = link.get_attribute("href")
            assert href and "/projects/" in href


class TestProjectFilter:
    @pytest.mark.parametrize("filter_val,required_tags", FILTER_CASES)
    def test_filter_hides_non_matching_cards(self, page, filter_val, required_tags):
        click_filter(page, filter_val)
        cards = page.find_elements(By.CSS_SELECTOR, ".project-card")
        for card in cards:
            tags = card.get_attribute("data-tags") or ""
            classes = card.get_attribute("class") or ""
            if any(tag in tags for tag in required_tags):
                assert "hidden" not in classes, (
                    f"Card with tags '{tags}' should be visible for filter '{filter_val}'"
                )
            else:
                assert "hidden" in classes, (
                    f"Card with tags '{tags}' should be hidden for filter '{filter_val}'"
                )

    def test_filter_all_restores_all_cards(self, page):
        # Start from a filtered state
        click_filter(page, "ai")
        click_filter(page, "all")
        assert len(visible_cards(page)) == EXPECTED_CARD_COUNT

    def test_active_filter_button_gets_active_class(self, page):
        click_filter(page, "audio")
        active_btns = page.find_elements(By.CSS_SELECTOR, ".filter-btn.active")
        assert len(active_btns) == 1
        assert active_btns[0].get_attribute("data-filter") == "audio"
        # Reset
        click_filter(page, "all")
