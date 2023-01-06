#include "spi_flash.h"

#include <stdio.h>
#include <generated/csr.h>
#include <generated/mem.h>

#include "spi_flash_csr.h"

/*-----------------------------------------------------------------------*/
/* Constants                                                             */
/*-----------------------------------------------------------------------*/

#define SPI_FLASH_READ_ID 0x9F
#define SPI_FLASH_READ    0x03
#define SPI_FLASH_WREN    0x06
#define SPI_FLASH_WRDI    0x04
#define SPI_FLASH_PP      0x02
#define SPI_FLASH_SE      0xD8
#define SPI_FLASH_FE      0xC7
#define SPI_FLASH_RDSR    0x05
#define SPI_FLASH_WRSR    0x01
#define SPI_FLASH_SR      0x44
/* status */
#define SPI_FLASH_WIP     0x01

#define SPI_FLASH_SECTOR_SIZE (1 << 12)

#define SPI_CONFIG_LEN   (1 << 0)
#define SPI_CONFIG_WIDTH (1 << 8)
#define SPI_CONFIG_MASK  (1 << 16)

#define SPI_STATUS_TX_READY (1 << 0)
#define SPI_STATUS_RX_READY (1 << 0)

/*-----------------------------------------------------------------------*/
/* Flash Bitbang Access                                                  */
/*-----------------------------------------------------------------------*/

static uint32_t spi_flash_xfer(int tx_len, uint8_t cmd, uint32_t tx_data) {
    uint32_t rx_data;

    /* Be sure to empty RX queue before doing Xfer. */
    while (spiflash_core_master_status_rx_ready_read())
      spiflash_core_master_rxtx_read();

    /* Configure PHY */

    /* Set CS */
    spiflash_core_master_cs_write(1);

    /* Send Cmd */
    spiflash_core_master_phyconfig_write(
        8 * SPI_CONFIG_LEN   |
        1 * SPI_CONFIG_WIDTH |
      0b1 * SPI_CONFIG_MASK
    );
    spiflash_core_master_rxtx_write(cmd);
    while ((spiflash_core_master_status_read() & SPI_STATUS_RX_READY) == 0);

    /* Send Data */
    spiflash_core_master_phyconfig_write(
        (tx_len - 8) * SPI_CONFIG_LEN   |
                   1 * SPI_CONFIG_WIDTH |
                 0b1 * SPI_CONFIG_MASK
    );
    spiflash_core_master_rxtx_write(tx_data);
    while ((spiflash_core_master_status_read() & SPI_STATUS_RX_READY) == 0);
    rx_data = spiflash_core_master_rxtx_read();

    /* Reset CS */
    spiflash_core_master_cs_write(0);

    return rx_data;
}

static uint32_t spi_flash_read_id(void) {
    return spi_flash_xfer(32, SPI_FLASH_READ_ID, 0) & 0xffffff;
}

static void spi_flash_write_enable(void) {
    spi_flash_xfer(8, SPI_FLASH_WREN, 0);
}

static void spi_flash_write_disable(void) {
    spi_flash_xfer(8, SPI_FLASH_WRDI, 0);
}

static uint8_t spi_flash_read_status(void) {
    return spi_flash_xfer(16, SPI_FLASH_RDSR, 0) & 0xff;
}

static void spi_flash_write(uint32_t addr, uint8_t byte) {
    spi_flash_xfer(40, SPI_FLASH_PP, (addr << 8) | byte);
}

static void spi_flash_write_buf(const uint8_t *buf, uint32_t base, uint32_t size) {
    int i;

    /* Program */
    for(i = 0; i < size; i++) {
        printf("Writing %08lx\r", base + i);
        while (spi_flash_read_status() & SPI_FLASH_WIP) {
            busy_wait(1000);
        }
        spi_flash_write_enable();
        spi_flash_write(base + i, buf[i]);
        spi_flash_write_disable();
    }
    printf("\n");
}

/*-----------------------------------------------------------------------*/
/* Flash Tests                                                           */
/*-----------------------------------------------------------------------*/

static void spi_flash_dummy_read(void) {
  volatile uint32_t *axi_spi_flash = (uint32_t *) AXIL_QUADSPI_MMAP_BASE;
  /* Initial dummy reads; seems required by model */
  __attribute__((unused)) uint8_t dummy = axi_spi_flash[0];
}

void test_spi_flash_mmap(void) {
  volatile uint32_t *axi_spi_flash = (uint32_t *) AXIL_QUADSPI_MMAP_BASE;
  spi_flash_dummy_read();
  printf("SPI Flash Dump:\n");
  for (int i=0; i<28; i++) {
    printf("0x%08x: 0x%08lx\n", 4*i, axi_spi_flash[i]);
  }
}

void test_spi_flash_program(void) {
  uint32_t buffer[2];
  spi_flash_dummy_read();
  buffer[0] = 0x5aa55aa5;
  buffer[1] = 0xffffffff;
  spi_flash_write_buf((uint8_t*)&buffer, 0x00000000, 8);
  spi_flash_write_buf((uint8_t*)&buffer, 0x00000004, 9);
  spi_flash_write_buf((uint8_t*)&buffer, 0x00000001c, 12);}
